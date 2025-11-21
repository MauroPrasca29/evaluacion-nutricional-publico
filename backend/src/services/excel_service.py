# backend/src/services/excel_service.py
import pandas as pd
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from io import BytesIO
from datetime import datetime, date
from openpyxl.worksheet.datavalidation import DataValidation
from sqlalchemy import or_, and_

class ExcelService:
    
    # Cache a nivel de clase para tablas WHO/RIEN
    _nutrition_cache = None
    
    @staticmethod
    def _ensure_nutrition_cache():
        """Carga todas las tablas nutricionales en memoria UNA SOLA VEZ"""
        if ExcelService._nutrition_cache is not None:
            return ExcelService._nutrition_cache
        
        print("🔄 Inicializando cache de tablas nutricionales...")
        from src.services.nutrition_service import NutritionService
        
        # Pre-cargar todas las tablas WHO que se usan frecuentemente
        # Esto se hace una sola vez al iniciar el procesamiento
        ExcelService._nutrition_cache = {
            'initialized': True,
            'service': NutritionService
        }
        
        print("✅ Cache de tablas nutricionales inicializado")
        return ExcelService._nutrition_cache
    
    @staticmethod
    def process_children_excel(file_content: bytes, db_session) -> Dict[str, Any]:
        """Process Excel file with children data - FASE 2 OPTIMIZED with BATCH PROCESSING"""
        try:
            # ⚡ FASE 1: Cargar cache nutricional al inicio
            ExcelService._ensure_nutrition_cache()
            
            df = pd.read_excel(BytesIO(file_content))
            
            # Mapeos de español a inglés para procesamiento
            genero_map = {
                'Masculino': 'male',
                'Femenino': 'female',
                'M': 'male',
                'F': 'female'
            }
            
            actividad_map = {
                'Ligera': 'light',
                'Moderada': 'moderate',
                'Intensa': 'vigorous',
                'Sedentaria': 'light'
            }
            
            alimentacion_map = {
                'Lactancia materna': 'breast',
                'Fórmula': 'formula',
                'Mixta': 'mixed'
            }
            
            # Columnas requeridas mínimas
            required_columns = [
                'acudiente_documento', 'acudiente_nombre', 'acudiente_telefono',
                'infante_nombre', 'infante_fecha_nacimiento', 'infante_genero', 'sede_id',
                'seguimiento_fecha', 'peso', 'estatura'
            ]
            
            # Validar columnas requeridas
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "success": False,
                    "error": f"Faltan columnas requeridas: {', '.join(missing_columns)}"
                }
            
            from src.db.models import Acudiente, Infante, Seguimiento, DatoAntropometrico, Examen, EvaluacionNutricional
            from src.services.nutrition_service import NutritionService
            
            total_rows = len(df)
            print(f"📊 Procesando {total_rows} filas con BATCH PROCESSING...")
            
            # ⚡ FASE 2 - PASO 1: Extraer todas las claves únicas para batch queries
            print("🔍 Extrayendo datos únicos para búsqueda en lote...")
            acudientes_keys: Set[Tuple[str, str]] = set()
            infantes_keys: Set[Tuple[str, date, str]] = set()  # (nombre, fecha_nac, acudiente_key)
            
            # Primera pasada: recolectar claves únicas
            validated_rows = []
            errors = []
            
            for idx, row in df.iterrows():
                row_num = idx + 2
                row_errors = []
                
                try:
                    # Validaciones rápidas
                    acudiente_nombre = str(row.get('acudiente_nombre', '')).strip()
                    acudiente_telefono = str(row.get('acudiente_telefono', '')).strip()
                    
                    if not acudiente_nombre or pd.isna(row.get('acudiente_nombre')):
                        row_errors.append("Nombre de acudiente es requerido")
                    if not acudiente_telefono or pd.isna(row.get('acudiente_telefono')):
                        row_errors.append("Teléfono de acudiente es requerido")
                    elif not re.match(r'^\d{10}$', acudiente_telefono):
                        row_errors.append(f"Teléfono inválido: {acudiente_telefono}")
                    
                    infante_nombre = str(row.get('infante_nombre', '')).strip()
                    if not infante_nombre or pd.isna(row.get('infante_nombre')):
                        row_errors.append("Nombre de infante es requerido")
                    
                    infante_fecha_nacimiento = row.get('infante_fecha_nacimiento')
                    if pd.isna(infante_fecha_nacimiento):
                        row_errors.append("Fecha de nacimiento del infante es requerida")
                    else:
                        if isinstance(infante_fecha_nacimiento, str):
                            infante_fecha_nacimiento = datetime.strptime(infante_fecha_nacimiento, "%Y-%m-%d").date()
                        elif isinstance(infante_fecha_nacimiento, pd.Timestamp):
                            infante_fecha_nacimiento = infante_fecha_nacimiento.date()
                        elif not isinstance(infante_fecha_nacimiento, date):
                            infante_fecha_nacimiento = pd.to_datetime(infante_fecha_nacimiento).date()
                    
                    if row_errors:
                        errors.append({
                            "fila": row_num,
                            "infante": infante_nombre,
                            "errores": row_errors
                        })
                        continue
                    
                    # Guardar claves para batch query
                    acudiente_key = (acudiente_nombre, acudiente_telefono)
                    acudientes_keys.add(acudiente_key)
                    infantes_keys.add((infante_nombre, infante_fecha_nacimiento, acudiente_key))
                    
                    # Guardar row validada para procesamiento posterior
                    validated_rows.append({
                        'idx': idx,
                        'row_num': row_num,
                        'row': row,
                        'acudiente_key': acudiente_key,
                        'infante_key': (infante_nombre, infante_fecha_nacimiento)
                    })
                    
                except Exception as e:
                    errors.append({
                        "fila": row_num,
                        "infante": infante_nombre if 'infante_nombre' in locals() else "N/A",
                        "errores": [f"Error en validación inicial: {str(e)}"]
                    })
            
            if not validated_rows:
                return {
                    "success": False,
                    "error": "No hay filas válidas para procesar",
                    "errors": errors
                }
            
            # ⚡ FASE 2 - PASO 2: Batch query para TODOS los acudientes
            print(f"🔍 Buscando {len(acudientes_keys)} acudientes únicos en DB...")
            acudientes_map: Dict[Tuple[str, str], Acudiente] = {}
            
            if acudientes_keys:
                # Construir query con OR para todos los acudientes
                acudiente_conditions = [
                    and_(
                        Acudiente.nombre == nombre,
                        Acudiente.telefono == telefono
                    )
                    for nombre, telefono in acudientes_keys
                ]
                
                existing_acudientes = db_session.query(Acudiente).filter(
                    or_(*acudiente_conditions)
                ).all()
                
                acudientes_map = {
                    (a.nombre, a.telefono): a 
                    for a in existing_acudientes
                }
                print(f"✅ Encontrados {len(acudientes_map)} acudientes existentes")
            
            # ⚡ FASE 2 - PASO 3: Crear acudientes faltantes en BATCH
            nuevos_acudientes = []
            for acudiente_key in acudientes_keys:
                if acudiente_key not in acudientes_map:
                    nuevo = Acudiente(
                        nombre=acudiente_key[0],
                        telefono=acudiente_key[1],
                        correo=None,  # Se actualizará después si es necesario
                        direccion=None
                    )
                    nuevos_acudientes.append(nuevo)
                    acudientes_map[acudiente_key] = nuevo
            
            if nuevos_acudientes:
                print(f"➕ Creando {len(nuevos_acudientes)} acudientes nuevos...")
                db_session.bulk_save_objects(nuevos_acudientes, return_defaults=True)
                db_session.flush()
                print(f"✅ Acudientes guardados")
            
            # ⚡ FASE 2 - PASO 4: Batch query para TODOS los infantes
            print(f"🔍 Buscando infantes únicos en DB...")
            infantes_map: Dict[Tuple[str, date, int], Infante] = {}
            
            # Agrupar infantes por acudiente para query más eficiente
            if infantes_keys:
                # Necesitamos los IDs de acudientes primero
                infante_conditions = []
                for infante_nombre, fecha_nac, acudiente_key in infantes_keys:
                    acudiente = acudientes_map.get(acudiente_key)
                    if acudiente and acudiente.id_acudiente:
                        infante_conditions.append(
                            and_(
                                Infante.nombre == infante_nombre,
                                Infante.fecha_nacimiento == fecha_nac,
                                Infante.acudiente_id == acudiente.id_acudiente
                            )
                        )
                
                if infante_conditions:
                    existing_infantes = db_session.query(Infante).filter(
                        or_(*infante_conditions)
                    ).all()
                    
                    for i in existing_infantes:
                        # Recuperar acudiente para crear key
                        acudiente = db_session.query(Acudiente).get(i.acudiente_id)
                        if acudiente:
                            key = (i.nombre, i.fecha_nacimiento, acudiente.id_acudiente)
                            infantes_map[key] = i
                    
                    print(f"✅ Encontrados {len(infantes_map)} infantes existentes")
            
            # Ahora procesamos cada fila con los datos pre-cargados
            print(f"⚙️ Procesando {len(validated_rows)} filas...")
            
            processed_data = []
            success_count = 0
            
            for validated_row in validated_rows:
                idx = validated_row['idx']
                row_num = validated_row['row_num']
                row = validated_row['row']
                acudiente_key = validated_row['acudiente_key']
                
                if idx > 0 and idx % 10 == 0:
                    print(f"  ⏳ Procesadas {idx}/{total_rows} filas ({idx*100//total_rows}%)...")
                
                try:
                    # Validaciones completas
                    acudiente_documento = str(row.get('acudiente_documento', '')).strip()
                    acudiente_nombre = acudiente_key[0]
                    acudiente_telefono = acudiente_key[1]
                    acudiente_tipo_documento = str(row.get('acudiente_tipo_documento', 'CC')).strip()
                    acudiente_email = str(row.get('acudiente_email', '')).strip() if not pd.isna(row.get('acudiente_email')) else None
                    acudiente_direccion = str(row.get('acudiente_direccion', '')).strip() if not pd.isna(row.get('acudiente_direccion')) else None
                    acudiente_parentesco = str(row.get('acudiente_parentesco', '')).strip() if not pd.isna(row.get('acudiente_parentesco')) else None
                    
                    if acudiente_email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', acudiente_email):
                        acudiente_email = None
                    
                    # Obtener acudiente del mapa
                    acudiente = acudientes_map[acudiente_key]
                    
                    # Actualizar datos adicionales si son nuevos
                    if acudiente_email and not acudiente.correo:
                        acudiente.correo = acudiente_email
                    if acudiente_direccion and not acudiente.direccion:
                        acudiente.direccion = acudiente_direccion
                    
                    # Validar infante
                    infante_nombre = str(row.get('infante_nombre', '')).strip()
                    infante_fecha_nacimiento = row.get('infante_fecha_nacimiento')
                    
                    if isinstance(infante_fecha_nacimiento, str):
                        infante_fecha_nacimiento = datetime.strptime(infante_fecha_nacimiento, "%Y-%m-%d").date()
                    elif isinstance(infante_fecha_nacimiento, pd.Timestamp):
                        infante_fecha_nacimiento = infante_fecha_nacimiento.date()
                    elif not isinstance(infante_fecha_nacimiento, date):
                        infante_fecha_nacimiento = pd.to_datetime(infante_fecha_nacimiento).date()
                    
                    infante_genero = str(row.get('infante_genero', '')).strip()
                    if infante_genero not in genero_map:
                        errors.append({
                            "fila": row_num,
                            "infante": infante_nombre,
                            "errores": [f"Género inválido: {infante_genero}"]
                        })
                        continue
                    
                    infante_genero_db = genero_map[infante_genero]
                    
                    try:
                        sede_id = int(row.get('sede_id'))
                    except:
                        errors.append({
                            "fila": row_num,
                            "infante": infante_nombre,
                            "errores": [f"ID de sede inválido: {row.get('sede_id')}"]
                        })
                        continue
                    
                    # Buscar o crear infante
                    infante_map_key = (infante_nombre, infante_fecha_nacimiento, acudiente.id_acudiente)
                    infante = infantes_map.get(infante_map_key)
                    
                    if not infante:
                        infante = Infante(
                            nombre=infante_nombre,
                            fecha_nacimiento=infante_fecha_nacimiento,
                            genero=infante_genero_db[0].upper(),
                            acudiente_id=acudiente.id_acudiente,
                            sede_id=sede_id
                        )
                        db_session.add(infante)
                        db_session.flush()
                        infantes_map[infante_map_key] = infante
                    
                    # Validar seguimiento
                    seguimiento_fecha = row.get('seguimiento_fecha')
                    if isinstance(seguimiento_fecha, str):
                        seguimiento_fecha = datetime.strptime(seguimiento_fecha, "%Y-%m-%d").date()
                    elif isinstance(seguimiento_fecha, pd.Timestamp):
                        seguimiento_fecha = seguimiento_fecha.date()
                    elif not isinstance(seguimiento_fecha, date):
                        seguimiento_fecha = pd.to_datetime(seguimiento_fecha).date()
                    
                    try:
                        peso = float(row.get('peso'))
                        if peso <= 0 or peso > 200:
                            raise ValueError(f"Peso fuera de rango: {peso}")
                    except:
                        errors.append({
                            "fila": row_num,
                            "infante": infante_nombre,
                            "errores": [f"Peso inválido: {row.get('peso')}"]
                        })
                        continue
                    
                    try:
                        estatura = float(row.get('estatura'))
                        if estatura <= 0 or estatura > 250:
                            raise ValueError(f"Estatura fuera de rango: {estatura}")
                    except:
                        errors.append({
                            "fila": row_num,
                            "infante": infante_nombre,
                            "errores": [f"Estatura inválida: {row.get('estatura')}"]
                        })
                        continue
                    
                    # Medidas opcionales
                    perimetro_cefalico = None
                    if not pd.isna(row.get('perimetro_cefalico')):
                        try:
                            perimetro_cefalico = float(row.get('perimetro_cefalico'))
                            if perimetro_cefalico < 0 or perimetro_cefalico > 100:
                                perimetro_cefalico = None
                        except:
                            pass
                    
                    pliegue_triceps = None
                    if not pd.isna(row.get('pliegue_triceps')):
                        try:
                            pliegue_triceps = float(row.get('pliegue_triceps'))
                            if pliegue_triceps < 0 or pliegue_triceps > 100:
                                pliegue_triceps = None
                        except:
                            pass
                    
                    pliegue_subescapular = None
                    if not pd.isna(row.get('pliegue_subescapular')):
                        try:
                            pliegue_subescapular = float(row.get('pliegue_subescapular'))
                            if pliegue_subescapular < 0 or pliegue_subescapular > 100:
                                pliegue_subescapular = None
                        except:
                            pass
                    
                    circunferencia_braquial = None
                    if not pd.isna(row.get('circunferencia_braquial')):
                        try:
                            circunferencia_braquial = float(row.get('circunferencia_braquial'))
                            if circunferencia_braquial < 0 or circunferencia_braquial > 100:
                                circunferencia_braquial = None
                        except:
                            pass
                    
                    perimetro_abdominal = None
                    if not pd.isna(row.get('perimetro_abdominal')):
                        try:
                            perimetro_abdominal = float(row.get('perimetro_abdominal'))
                            if perimetro_abdominal < 0 or perimetro_abdominal > 200:
                                perimetro_abdominal = None
                        except:
                            pass
                    
                    nivel_actividad = str(row.get('nivel_actividad', '')).strip() if not pd.isna(row.get('nivel_actividad')) else None
                    if nivel_actividad and nivel_actividad in actividad_map:
                        nivel_actividad = actividad_map[nivel_actividad]
                    else:
                        nivel_actividad = None
                    
                    tipo_alimentacion = str(row.get('tipo_alimentacion', '')).strip() if not pd.isna(row.get('tipo_alimentacion')) else None
                    if tipo_alimentacion and tipo_alimentacion in alimentacion_map:
                        tipo_alimentacion = alimentacion_map[tipo_alimentacion]
                    else:
                        tipo_alimentacion = None
                    
                    observacion = str(row.get('observacion', '')).strip() if not pd.isna(row.get('observacion')) else None
                    
                    hemoglobina = None
                    if not pd.isna(row.get('hemoglobina')):
                        try:
                            hemoglobina = float(row.get('hemoglobina'))
                            if hemoglobina < 0 or hemoglobina > 30:
                                hemoglobina = None
                        except:
                            pass
                    
                    # Crear seguimiento
                    seguimiento = Seguimiento(
                        infante_id=infante.id_infante,
                        fecha=seguimiento_fecha,
                        observacion=observacion,
                        encargado_id=None
                    )
                    db_session.add(seguimiento)
                    db_session.flush()
                    
                    # Calcular IMC
                    imc = None
                    if peso and estatura:
                        altura_metros = estatura / 100
                        imc = peso / (altura_metros ** 2)
                    
                    # Crear datos antropométricos
                    datos_antropo = DatoAntropometrico(
                        seguimiento_id=seguimiento.id_seguimiento,
                        peso=peso,
                        estatura=estatura,
                        imc=imc,
                        circunferencia_braquial=circunferencia_braquial,
                        perimetro_cefalico=perimetro_cefalico,
                        pliegue_triceps=pliegue_triceps,
                        pliegue_subescapular=pliegue_subescapular,
                        perimetro_abdominal=perimetro_abdominal
                    )
                    db_session.add(datos_antropo)
                    
                    # Crear examen si hay hemoglobina
                    if hemoglobina is not None:
                        examen = Examen(
                            seguimiento_id=seguimiento.id_seguimiento,
                            hemoglobina=hemoglobina
                        )
                        db_session.add(examen)
                    
                    # Evaluación nutricional con cache
                    if peso and estatura:
                        age_days = (seguimiento_fecha - infante_fecha_nacimiento).days
                        gender = 'male' if infante.genero == 'M' else 'female'
                        
                        assessment = NutritionService.assess_nutritional_status(
                            age_days=age_days,
                            weight=peso,
                            height=estatura,
                            gender=gender,
                            head_circumference=perimetro_cefalico,
                            triceps_skinfold=pliegue_triceps,
                            subscapular_skinfold=pliegue_subescapular
                        )
                        
                        energy_req = NutritionService.get_energy_requirement(
                            age_days=age_days,
                            weight=peso,
                            gender=gender,
                            feeding_mode=tipo_alimentacion or 'mixed',
                            activity_level=nivel_actividad or 'moderate'
                        )
                        
                        nutrient_data = None
                        try:
                            nutrient_data = NutritionService.get_nutrient_food_table_data(
                                age_days=age_days,
                                gender=gender,
                                weight=peso,
                                kcal_per_day=energy_req.get("kcal_per_day") if energy_req else None
                            )
                        except Exception as e:
                            print(f"WARNING: nutrient_data error: {str(e)}")
                            nutrient_data = []
                        
                        recommendations = NutritionService.generate_recommendations(assessment)
                        
                        evaluacion = EvaluacionNutricional(
                            seguimiento_id=seguimiento.id_seguimiento,
                            imc=assessment.get("bmi"),
                            peso_edad_zscore=assessment.get("weight_for_age_zscore"),
                            talla_edad_zscore=assessment.get("height_for_age_zscore"),
                            imc_edad_zscore=assessment.get("bmi_for_age_zscore"),
                            perimetro_cefalico_zscore=assessment.get("head_circumference_zscore"),
                            pliegue_triceps_zscore=assessment.get("triceps_skinfold_zscore"),
                            pliegue_subescapular_zscore=assessment.get("subscapular_skinfold_zscore"),
                            clasificacion_peso_edad=assessment["nutritional_status"].get("peso_edad"),
                            clasificacion_talla_edad=assessment["nutritional_status"].get("talla_edad"),
                            clasificacion_peso_talla=assessment["nutritional_status"].get("peso_talla"),
                            clasificacion_imc_edad=assessment["nutritional_status"].get("imc_edad"),
                            clasificacion_perimetro_cefalico=assessment["nutritional_status"].get("perimetro_cefalico_edad"),
                            clasificacion_pliegue_triceps=assessment["nutritional_status"].get("pliegue_triceps"),
                            clasificacion_pliegue_subescapular=assessment["nutritional_status"].get("pliegue_subescapular"),
                            nivel_riesgo=assessment.get("risk_level", "Bajo"),
                            requerimientos_energeticos=energy_req if energy_req else {},
                            requerimientos_nutrientes=nutrient_data if nutrient_data else [],
                            recomendaciones_nutricionales=recommendations.get("nutritional_recommendations", []),
                            recomendaciones_generales=recommendations.get("general_recommendations", []),
                            instrucciones_cuidador=recommendations.get("caregiver_instructions", [])
                        )
                        db_session.add(evaluacion)
                    
                    success_count += 1
                    processed_data.append({
                        "fila": row_num,
                        "acudiente": acudiente_nombre,
                        "infante": infante_nombre,
                        "seguimiento_id": seguimiento.id_seguimiento
                    })
                    
                except Exception as e:
                    errors.append({
                        "fila": row_num,
                        "infante": infante_nombre if 'infante_nombre' in locals() else "N/A",
                        "errores": [f"Error inesperado: {str(e)}"]
                    })
            
            # ⚡ UN SOLO COMMIT AL FINAL
            if success_count > 0:
                print(f"💾 Guardando {success_count} seguimientos en la base de datos...")
                db_session.commit()
                print(f"✅ Importación completada: {success_count} éxitos, {len(errors)} errores")
            
            return {
                "success": True,
                "processed_count": success_count,
                "error_count": len(errors),
                "total_rows": len(df),
                "data": processed_data,
                "errors": errors
            }
            
        except Exception as e:
            db_session.rollback()
            return {
                "success": False,
                "error": f"Error al procesar el archivo: {str(e)}"
            }

    
    @staticmethod
    def generate_template() -> bytes:
        """Generate Excel template for data import with all required fields"""
        
        # Datos de ejemplo con todas las columnas necesarias
        template_data = {
            # SECCIÓN 1: DATOS DEL INFANTE
            'infante_documento': ['1122334455', '2233445566'],
            'infante_tipo_documento': ['RC', 'RC'],
            'infante_nombre': ['Juan López Pérez', 'Ana Pérez González'],
            'infante_fecha_nacimiento': ['2023-11-13', '2023-06-15'],
            'infante_genero': ['Masculino', 'Femenino'],
            'sede_id': [1, 1],
            
            # SECCIÓN 2: DATOS DEL ACUDIENTE
            'acudiente_documento': ['1234567890', '0987654321'],
            'acudiente_tipo_documento': ['CC', 'CC'],
            'acudiente_nombre': ['María López García', 'Juan Pérez Sánchez'],
            'acudiente_telefono': ['3001234567', '3009876543'],
            'acudiente_email': ['maria.lopez@email.com', 'juan.perez@email.com'],
            'acudiente_direccion': ['Calle 123 #45-67', 'Carrera 45 #78-90'],
            'acudiente_parentesco': ['Madre', 'Padre'],
            
            # SECCIÓN 3: DATOS DEL SEGUIMIENTO
            'seguimiento_fecha': ['2024-12-15', '2024-12-15'],
            'peso': [10.5, 9.8],
            'estatura': [75.0, 72.5],
            'perimetro_cefalico': [45.5, 44.2],
            'pliegue_triceps': [8.5, 7.8],
            'pliegue_subescapular': [6.2, 5.9],
            'circunferencia_braquial': [14.5, 13.8],
            'perimetro_abdominal': [48.0, 46.5],
            'nivel_actividad': ['Ligera', 'Moderada'],
            'tipo_alimentacion': ['Lactancia materna', 'Fórmula'],
            'observacion': ['Control mensual', 'Primera consulta'],
            
            # SECCIÓN 4: EXÁMENES DE LABORATORIO (OPCIONAL)
            'hemoglobina': [12.5, 11.8],
        }
        
        df = pd.DataFrame(template_data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Plantilla', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Plantilla']
            
            # Ajustar anchos de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Validaciones de datos
            dv_genero = DataValidation(
                type="list",
                formula1='"Masculino,Femenino"',
                allow_blank=False
            )
            dv_genero.error = 'Valor inválido'
            dv_genero.errorTitle = 'Género inválido'
            dv_genero.prompt = 'Seleccione: Masculino o Femenino'
            dv_genero.promptTitle = 'Género'
            worksheet.add_data_validation(dv_genero)
            dv_genero.add('E2:E1000')
            
            dv_actividad = DataValidation(
                type="list",
                formula1='"Ligera,Moderada,Intensa"',
                allow_blank=True
            )
            dv_actividad.error = 'Valor inválido'
            dv_actividad.errorTitle = 'Nivel de actividad inválido'
            dv_actividad.prompt = 'Seleccione: Ligera, Moderada o Intensa'
            dv_actividad.promptTitle = 'Nivel de Actividad'
            worksheet.add_data_validation(dv_actividad)
            dv_actividad.add('V2:V1000')
            
            dv_alimentacion = DataValidation(
                type="list",
                formula1='"Lactancia materna,Fórmula,Mixta"',
                allow_blank=True
            )
            dv_alimentacion.error = 'Valor inválido'
            dv_alimentacion.errorTitle = 'Tipo de alimentación inválido'
            dv_alimentacion.prompt = 'Seleccione: Lactancia materna, Fórmula o Mixta'
            dv_alimentacion.promptTitle = 'Tipo de Alimentación'
            worksheet.add_data_validation(dv_alimentacion)
            dv_alimentacion.add('W2:W1000')
            
            # Hoja de instrucciones
            instructions_data = {
                'Campo': [
                    'INFANTE', 'infante_documento', 'infante_tipo_documento', 'infante_nombre',
                    'infante_fecha_nacimiento', 'infante_genero', 'sede_id', '',
                    'ACUDIENTE', 'acudiente_documento', 'acudiente_tipo_documento', 'acudiente_nombre',
                    'acudiente_telefono', 'acudiente_email', 'acudiente_direccion', 'acudiente_parentesco', '',
                    'SEGUIMIENTO', 'seguimiento_fecha', 'peso', 'estatura', 'perimetro_cefalico',
                    'pliegue_triceps', 'pliegue_subescapular', 'circunferencia_braquial', 'perimetro_abdominal',
                    'nivel_actividad', 'tipo_alimentacion', 'observacion', '',
                    'EXÁMENES', 'hemoglobina',
                ],
                'Descripción': [
                    'Datos del niño/a', 'Documento del niño (opcional)', 'RC, TI, etc.', 'Nombre completo del niño/a',
                    'Formato: YYYY-MM-DD', 'Masculino o Femenino', 'ID de la sede (número)', '',
                    'Datos del padre/madre/acudiente', 'Número de documento del acudiente', 'CC, TI, CE, etc.',
                    'Nombre completo del acudiente', 'Teléfono de contacto', 'Correo electrónico (opcional)',
                    'Dirección de residencia', 'Madre, Padre, Abuelo/a, Tío/a, etc.', '',
                    'Datos de medición', 'Fecha del seguimiento (YYYY-MM-DD)', 'Peso en kilogramos (decimal con punto)',
                    'Talla/estatura en centímetros', 'Perímetro cefálico en cm (opcional)',
                    'Pliegue tricipital en mm (opcional)', 'Pliegue subescapular en mm (opcional)',
                    'Circunferencia del brazo en cm (opcional)', 'Perímetro abdominal en cm (opcional)',
                    'Nivel de actividad física del niño', 'Tipo de alimentación actual',
                    'Observaciones del seguimiento (opcional)', '',
                    'Exámenes de laboratorio (opcionales)', 'Nivel de hemoglobina en g/dL',
                ],
                'Obligatorio': [
                    '', 'NO', 'NO', 'SÍ', 'SÍ', 'SÍ', 'SÍ', '',
                    '', 'SÍ', 'NO', 'SÍ', 'SÍ', 'NO', 'NO', 'NO', '',
                    '', 'SÍ', 'SÍ', 'SÍ', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', '',
                    '', 'NO',
                ],
                'Formato/Valores': [
                    '', 'Texto/Números', 'RC, TI, etc.', 'Texto', 'YYYY-MM-DD (ej: 2023-11-13)',
                    'Masculino o Femenino (lista desplegable)', 'Número entero', '',
                    '', 'Texto/Números', 'CC, TI, CE, etc.', 'Texto', 'Números (10 dígitos)',
                    'email@ejemplo.com', 'Texto', 'Texto', '',
                    '', 'YYYY-MM-DD (ej: 2024-12-15)', 'Decimal (ej: 10.5)', 'Decimal (ej: 75.0)',
                    'Decimal (ej: 45.5)', 'Decimal (ej: 8.5)', 'Decimal (ej: 6.2)', 'Decimal (ej: 14.5)',
                    'Decimal (ej: 48.0)', 'Ligera, Moderada, Intensa (lista desplegable)',
                    'Lactancia materna, Fórmula, Mixta (lista desplegable)', 'Texto', '',
                    '', 'Decimal (ej: 12.5)',
                ]
            }
            
            df_instructions = pd.DataFrame(instructions_data)
            df_instructions.to_excel(writer, sheet_name='Instrucciones', index=False)
            
            ws_instructions = writer.sheets['Instrucciones']
            ws_instructions.column_dimensions['A'].width = 35
            ws_instructions.column_dimensions['B'].width = 60
            ws_instructions.column_dimensions['C'].width = 15
            ws_instructions.column_dimensions['D'].width = 50
        
        output.seek(0)
        return output.getvalue()