# Excel processing service
import pandas as pd
from typing import List, Dict, Any, Optional
from io import BytesIO
from datetime import datetime, date
from openpyxl.worksheet.datavalidation import DataValidation
import re

class ExcelService:
    
    @staticmethod
    def process_children_excel(file_content: bytes, db_session) -> Dict[str, Any]:
        """Process Excel file with children data with comprehensive validation"""
        try:
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
            
            processed_data = []
            errors = []
            success_count = 0
            
            for idx, row in df.iterrows():
                row_num = idx + 2  # Excel starts at row 2 (after header)
                row_errors = []
                
                try:
                    # ===== VALIDACIONES ACUDIENTE =====
                    acudiente_documento = str(row.get('acudiente_documento', '')).strip()
                    if not acudiente_documento or pd.isna(row.get('acudiente_documento')):
                        row_errors.append("Documento de acudiente es requerido")
                    
                    acudiente_nombre = str(row.get('acudiente_nombre', '')).strip()
                    if not acudiente_nombre or pd.isna(row.get('acudiente_nombre')):
                        row_errors.append("Nombre de acudiente es requerido")
                    
                    acudiente_telefono = str(row.get('acudiente_telefono', '')).strip()
                    if not acudiente_telefono or pd.isna(row.get('acudiente_telefono')):
                        row_errors.append("Teléfono de acudiente es requerido")
                    elif not re.match(r'^\d{10}$', acudiente_telefono):
                        row_errors.append(f"Teléfono de acudiente inválido (debe tener 10 dígitos): {acudiente_telefono}")
                    
                    acudiente_tipo_documento = str(row.get('acudiente_tipo_documento', 'CC')).strip()
                    acudiente_email = str(row.get('acudiente_email', '')).strip() if not pd.isna(row.get('acudiente_email')) else None
                    acudiente_direccion = str(row.get('acudiente_direccion', '')).strip() if not pd.isna(row.get('acudiente_direccion')) else None
                    acudiente_parentesco = str(row.get('acudiente_parentesco', '')).strip() if not pd.isna(row.get('acudiente_parentesco')) else None
                    
                    # Validar email si se proporciona
                    if acudiente_email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', acudiente_email):
                        row_errors.append(f"Email de acudiente inválido: {acudiente_email}")
                    
                    # ===== VALIDACIONES INFANTE =====
                    infante_nombre = str(row.get('infante_nombre', '')).strip()
                    if not infante_nombre or pd.isna(row.get('infante_nombre')):
                        row_errors.append("Nombre de infante es requerido")
                    
                    # Validar fecha de nacimiento
                    infante_fecha_nacimiento = row.get('infante_fecha_nacimiento')
                    if pd.isna(infante_fecha_nacimiento):
                        row_errors.append("Fecha de nacimiento del infante es requerida")
                    else:
                        try:
                            if isinstance(infante_fecha_nacimiento, str):
                                infante_fecha_nacimiento = datetime.strptime(infante_fecha_nacimiento, "%Y-%m-%d").date()
                            elif isinstance(infante_fecha_nacimiento, pd.Timestamp):
                                infante_fecha_nacimiento = infante_fecha_nacimiento.date()
                            elif not isinstance(infante_fecha_nacimiento, date):
                                infante_fecha_nacimiento = pd.to_datetime(infante_fecha_nacimiento).date()
                        except Exception as e:
                            row_errors.append(f"Fecha de nacimiento inválida (formato: YYYY-MM-DD): {infante_fecha_nacimiento}")
                    
                    # Validar género
                    infante_genero = str(row.get('infante_genero', '')).strip()
                    if not infante_genero or pd.isna(row.get('infante_genero')):
                        row_errors.append("Género del infante es requerido")
                    elif infante_genero not in genero_map:
                        row_errors.append(f"Género inválido (debe ser Masculino o Femenino): {infante_genero}")
                    else:
                        infante_genero_db = genero_map[infante_genero]
                    
                    # Validar sede_id
                    try:
                        sede_id = int(row.get('sede_id'))
                    except:
                        row_errors.append(f"ID de sede inválido (debe ser un número entero): {row.get('sede_id')}")
                        sede_id = None
                    
                    infante_documento = str(row.get('infante_documento', '')).strip() if not pd.isna(row.get('infante_documento')) else None
                    infante_tipo_documento = str(row.get('infante_tipo_documento', 'RC')).strip()
                    
                    # ===== VALIDACIONES SEGUIMIENTO =====
                    seguimiento_fecha = row.get('seguimiento_fecha')
                    if pd.isna(seguimiento_fecha):
                        row_errors.append("Fecha de seguimiento es requerida")
                    else:
                        try:
                            if isinstance(seguimiento_fecha, str):
                                seguimiento_fecha = datetime.strptime(seguimiento_fecha, "%Y-%m-%d").date()
                            elif isinstance(seguimiento_fecha, pd.Timestamp):
                                seguimiento_fecha = seguimiento_fecha.date()
                            elif not isinstance(seguimiento_fecha, date):
                                seguimiento_fecha = pd.to_datetime(seguimiento_fecha).date()
                        except Exception as e:
                            row_errors.append(f"Fecha de seguimiento inválida (formato: YYYY-MM-DD): {seguimiento_fecha}")
                    
                    # Validar peso
                    try:
                        peso = float(row.get('peso'))
                        if peso <= 0 or peso > 200:
                            row_errors.append(f"Peso inválido (debe estar entre 0 y 200 kg): {peso}")
                    except:
                        row_errors.append(f"Peso inválido (debe ser un número decimal): {row.get('peso')}")
                        peso = None
                    
                    # Validar estatura
                    try:
                        estatura = float(row.get('estatura'))
                        if estatura <= 0 or estatura > 250:
                            row_errors.append(f"Estatura inválida (debe estar entre 0 y 250 cm): {estatura}")
                    except:
                        row_errors.append(f"Estatura inválida (debe ser un número decimal): {row.get('estatura')}")
                        estatura = None
                    
                    # Validar medidas opcionales
                    perimetro_cefalico = None
                    if not pd.isna(row.get('perimetro_cefalico')):
                        try:
                            perimetro_cefalico = float(row.get('perimetro_cefalico'))
                            if perimetro_cefalico < 0 or perimetro_cefalico > 100:
                                row_errors.append(f"Perímetro cefálico inválido: {perimetro_cefalico}")
                                perimetro_cefalico = None
                        except:
                            row_errors.append(f"Perímetro cefálico inválido (debe ser decimal): {row.get('perimetro_cefalico')}")
                    
                    pliegue_triceps = None
                    if not pd.isna(row.get('pliegue_triceps')):
                        try:
                            pliegue_triceps = float(row.get('pliegue_triceps'))
                            if pliegue_triceps < 0 or pliegue_triceps > 100:
                                row_errors.append(f"Pliegue tricipital inválido: {pliegue_triceps}")
                                pliegue_triceps = None
                        except:
                            row_errors.append(f"Pliegue tricipital inválido (debe ser decimal): {row.get('pliegue_triceps')}")
                                                
                    pliegue_subescapular = None
                    if not pd.isna(row.get('pliegue_subescapular')):
                        try:
                            pliegue_subescapular = float(row.get('pliegue_subescapular'))
                            if pliegue_subescapular < 0 or pliegue_subescapular > 100:
                                row_errors.append(f"Pliegue subescapular inválido: {pliegue_subescapular}")
                                pliegue_subescapular = None
                        except:
                            row_errors.append(f"Pliegue subescapular inválido (debe ser decimal): {row.get('pliegue_subescapular')}")
                    
                    circunferencia_braquial = None
                    if not pd.isna(row.get('circunferencia_braquial')):
                        try:
                            circunferencia_braquial = float(row.get('circunferencia_braquial'))
                            if circunferencia_braquial < 0 or circunferencia_braquial > 100:
                                row_errors.append(f"Circunferencia braquial inválida: {circunferencia_braquial}")
                                circunferencia_braquial = None
                        except:
                            row_errors.append(f"Circunferencia braquial inválida (debe ser decimal): {row.get('circunferencia_braquial')}")
                    
                    perimetro_abdominal = None
                    if not pd.isna(row.get('perimetro_abdominal')):
                        try:
                            perimetro_abdominal = float(row.get('perimetro_abdominal'))
                            if perimetro_abdominal < 0 or perimetro_abdominal > 200:
                                row_errors.append(f"Perímetro abdominal inválido: {perimetro_abdominal}")
                                perimetro_abdominal = None
                        except:
                            row_errors.append(f"Perímetro abdominal inválido (debe ser decimal): {row.get('perimetro_abdominal')}")
                    
                    # Validar nivel de actividad
                    nivel_actividad = str(row.get('nivel_actividad', '')).strip() if not pd.isna(row.get('nivel_actividad')) else None
                    if nivel_actividad and nivel_actividad not in actividad_map:
                        row_errors.append(f"Nivel de actividad inválido (debe ser Ligera, Moderada o Intensa): {nivel_actividad}")
                        nivel_actividad = None
                    elif nivel_actividad:
                        nivel_actividad = actividad_map[nivel_actividad]
                    
                    # Validar tipo de alimentación
                    tipo_alimentacion = str(row.get('tipo_alimentacion', '')).strip() if not pd.isna(row.get('tipo_alimentacion')) else None
                    if tipo_alimentacion and tipo_alimentacion not in alimentacion_map:
                        row_errors.append(f"Tipo de alimentación inválido (debe ser Lactancia materna, Fórmula o Mixta): {tipo_alimentacion}")
                        tipo_alimentacion = None
                    elif tipo_alimentacion:
                        tipo_alimentacion = alimentacion_map[tipo_alimentacion]
                    
                    observacion = str(row.get('observacion', '')).strip() if not pd.isna(row.get('observacion')) else None
                    
                    # Validar hemoglobina
                    hemoglobina = None
                    if not pd.isna(row.get('hemoglobina')):
                        try:
                            hemoglobina = float(row.get('hemoglobina'))
                            if hemoglobina < 0 or hemoglobina > 30:
                                row_errors.append(f"Hemoglobina inválida (debe estar entre 0 y 30 g/dL): {hemoglobina}")
                                hemoglobina = None
                        except:
                            row_errors.append(f"Hemoglobina inválida (debe ser decimal): {row.get('hemoglobina')}")
                    
                    # Si hay errores de validación, agregar a la lista de errores y continuar
                    if row_errors:
                        errors.append({
                            "fila": row_num,
                            "infante": infante_nombre if 'infante_nombre' in locals() else "N/A",
                            "errores": row_errors
                        })
                        continue
                    
                    # ===== PROCESAMIENTO EN BASE DE DATOS =====
                    
                    # 1. Buscar o crear acudiente
                    acudiente = db_session.query(Acudiente).filter(
                        Acudiente.nombre == acudiente_nombre,
                        Acudiente.telefono == acudiente_telefono
                    ).first()
                    
                    if not acudiente:
                        acudiente = Acudiente(
                            nombre=acudiente_nombre,
                            telefono=acudiente_telefono,
                            correo=acudiente_email,
                            direccion=acudiente_direccion
                        )
                        db_session.add(acudiente)
                        db_session.flush()
                    
                    # 2. Buscar o crear infante
                    infante = db_session.query(Infante).filter(
                        Infante.nombre == infante_nombre,
                        Infante.fecha_nacimiento == infante_fecha_nacimiento,
                        Infante.acudiente_id == acudiente.id_acudiente
                    ).first()
                    
                    if not infante:
                        infante = Infante(
                            nombre=infante_nombre,
                            fecha_nacimiento=infante_fecha_nacimiento,
                            genero=infante_genero_db[0].upper(),  # 'M' o 'F'
                            acudiente_id=acudiente.id_acudiente,
                            sede_id=sede_id
                        )
                        db_session.add(infante)
                        db_session.flush()
                    
                    # 3. Crear seguimiento
                    seguimiento = Seguimiento(
                        infante_id=infante.id_infante,
                        fecha=seguimiento_fecha,
                        observacion=observacion,
                        encargado_id=None
                    )
                    db_session.add(seguimiento)
                    db_session.flush()
                    
                    # 4. Calcular IMC
                    imc = None
                    if peso and estatura:
                        altura_metros = estatura / 100
                        imc = peso / (altura_metros ** 2)
                    
                    # 5. Crear datos antropométricos
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
                    
                    # 6. Crear examen si hay hemoglobina
                    if hemoglobina is not None:
                        examen = Examen(
                            seguimiento_id=seguimiento.id_seguimiento,
                            hemoglobina=hemoglobina
                        )
                        db_session.add(examen)
                    
                    # 7. Realizar evaluación nutricional
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
                            if not nutrient_data:
                                print(f"WARNING: get_nutrient_food_table_data retornó vacío/None")
                        except Exception as e:
                            print(f"ERROR al obtener nutrient_data: {str(e)}")
                            nutrient_data = []
                        
                        recommendations = NutritionService.generate_recommendations(assessment)
                        
                        # Guardar evaluación
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
                        db_session.flush()  # Asegurar que se guarde antes de continuar
                    
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
            
            # Commit solo si hubo al menos un registro exitoso
            if success_count > 0:
                db_session.commit()
            
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
        # ORDEN: Primero infantes, luego acudientes
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
        
        # Crear DataFrame
        df = pd.DataFrame(template_data)
        
        # Crear Excel con formato
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Plantilla', index=False)
            
            # Obtener el workbook y worksheet para formatear
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
            
            # AGREGAR VALIDACIONES DE DATOS (LISTAS DESPLEGABLES)
            
            # 1. Género (columna E - infante_genero)
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
            dv_genero.add('E2:E1000')  # Aplicar a las primeras 1000 filas
            
            # 2. Nivel de actividad (columna V - nivel_actividad)
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
            
            # 3. Tipo de alimentación (columna W - tipo_alimentacion)
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
            
            # Agregar hoja de instrucciones
            instructions_data = {
                'Campo': [
                    'INFANTE',
                    'infante_documento',
                    'infante_tipo_documento',
                    'infante_nombre',
                    'infante_fecha_nacimiento',
                    'infante_genero',
                    'sede_id',
                    '',
                    'ACUDIENTE',
                    'acudiente_documento',
                    'acudiente_tipo_documento',
                    'acudiente_nombre',
                    'acudiente_telefono',
                    'acudiente_email',
                    'acudiente_direccion',
                    'acudiente_parentesco',
                    '',
                    'SEGUIMIENTO',
                    'seguimiento_fecha',
                    'peso',
                    'estatura',
                    'perimetro_cefalico',
                    'pliegue_triceps',
                    'pliegue_subescapular',
                    'circunferencia_braquial',
                    'perimetro_abdominal',
                    'nivel_actividad',
                    'tipo_alimentacion',
                    'observacion',
                    '',
                    'EXÁMENES',
                    'hemoglobina',
                ],
                'Descripción': [
                    'Datos del niño/a',
                    'Documento del niño (opcional si es muy pequeño)',
                    'RC, TI, etc.',
                    'Nombre completo del niño/a',
                    'Formato: YYYY-MM-DD',
                    'Masculino o Femenino',
                    'ID de la sede (número)',
                    '',
                    'Datos del padre/madre/acudiente',
                    'Número de documento del acudiente',
                    'CC, TI, CE, etc.',
                    'Nombre completo del acudiente',
                    'Teléfono de contacto',
                    'Correo electrónico (opcional)',
                    'Dirección de residencia',
                    'Madre, Padre, Abuelo/a, Tío/a, etc.',
                    '',
                    'Datos de medición',
                    'Fecha del seguimiento (YYYY-MM-DD)',
                    'Peso en kilogramos (decimal con punto)',
                    'Talla/estatura en centímetros',
                    'Perímetro cefálico en cm (opcional)',
                    'Pliegue tricipital en mm (opcional)',
                    'Pliegue subescapular en mm (opcional)',
                    'Circunferencia del brazo en cm (opcional)',
                    'Perímetro abdominal en cm (opcional)',
                    'Nivel de actividad física del niño',
                    'Tipo de alimentación actual',
                    'Observaciones del seguimiento (opcional)',
                    '',
                    'Exámenes de laboratorio (opcionales)',
                    'Nivel de hemoglobina en g/dL',
                ],
                'Obligatorio': [
                    '',
                    'NO',
                    'NO',
                    'SÍ',
                    'SÍ',
                    'SÍ',
                    'SÍ',
                    '',
                    '',
                    'SÍ',
                    'NO',
                    'SÍ',
                    'SÍ',
                    'NO',
                    'NO',
                    'NO',
                    '',
                    '',
                    'SÍ',
                    'SÍ',
                    'SÍ',
                    'NO',
                    'NO',
                    'NO',
                    'NO',
                    'NO',
                    'NO',
                    'NO',
                    'NO',
                    '',
                    '',
                    'NO',
                ],
                'Formato/Valores': [
                    '',
                    'Texto/Números',
                    'RC, TI, etc.',
                    'Texto',
                    'YYYY-MM-DD (ej: 2023-11-13)',
                    'Masculino o Femenino (lista desplegable)',
                    'Número entero',
                    '',
                    '',
                    'Texto/Números',
                    'CC, TI, CE, etc.',
                    'Texto',
                    'Números (10 dígitos)',
                    'email@ejemplo.com',
                    'Texto',
                    'Texto',
                    '',
                    '',
                    'YYYY-MM-DD (ej: 2024-12-15)',
                    'Decimal (ej: 10.5)',
                    'Decimal (ej: 75.0)',
                    'Decimal (ej: 45.5)',
                    'Decimal (ej: 8.5)',
                    'Decimal (ej: 6.2)',
                    'Decimal (ej: 14.5)',
                    'Decimal (ej: 48.0)',
                    'Ligera, Moderada, Intensa (lista desplegable)',
                    'Lactancia materna, Fórmula, Mixta (lista desplegable)',
                    'Texto',
                    '',
                    '',
                    'Decimal (ej: 12.5)',
                ]
            }
            
            df_instructions = pd.DataFrame(instructions_data)
            df_instructions.to_excel(writer, sheet_name='Instrucciones', index=False)
            
            # Ajustar anchos en hoja de instrucciones
            ws_instructions = writer.sheets['Instrucciones']
            ws_instructions.column_dimensions['A'].width = 35
            ws_instructions.column_dimensions['B'].width = 60
            ws_instructions.column_dimensions['C'].width = 15
            ws_instructions.column_dimensions['D'].width = 50
        
        output.seek(0)
        return output.getvalue()