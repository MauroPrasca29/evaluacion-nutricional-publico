from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel

from src.db.session import get_db
from src.db.models import Seguimiento, DatoAntropometrico, Examen, EvaluacionNutricional
from src.services.nutrition_service import NutritionService

router = APIRouter()

class FollowupCreate(BaseModel):
    infante_id: int
    fecha: date
    observacion: Optional[str] = None
    observaciones_clinicas: List[str] = []
    peso: Optional[float] = None
    estatura: Optional[float] = None
    circunferencia_braquial: Optional[float] = None
    perimetro_cefalico: Optional[float] = None
    pliegue_cutaneo: Optional[float] = None
    perimetro_abdominal: Optional[float] = None
    hemoglobina: Optional[float] = None
    foto_ojo_url: Optional[str] = None

@router.post("/")
def create_followup(followup_data: FollowupCreate, db: Session = Depends(get_db)):
    try:
        # Concatenar observaciones
        observaciones_texto = ", ".join(followup_data.observaciones_clinicas)
        if followup_data.observacion:
            observaciones_texto = f"{observaciones_texto}. {followup_data.observacion}" if observaciones_texto else followup_data.observacion
        
        # Crear seguimiento
        nuevo_seguimiento = Seguimiento(
            infante_id=followup_data.infante_id,
            fecha=followup_data.fecha,
            observacion=observaciones_texto,
            encargado_id=None  # TODO: obtener del usuario autenticado
        )
        db.add(nuevo_seguimiento)
        db.flush()
        
        # Calcular IMC si no viene
        imc = followup_data.imc if hasattr(followup_data, 'imc') else None
        if not imc and followup_data.peso and followup_data.estatura:
            altura_metros = followup_data.estatura / 100
            imc = followup_data.peso / (altura_metros ** 2)
        
        # Crear datos antropométricos
        datos_antropo = DatoAntropometrico(
            seguimiento_id=nuevo_seguimiento.id_seguimiento,
            peso=followup_data.peso,
            estatura=followup_data.estatura,
            imc=imc,
            circunferencia_braquial=followup_data.circunferencia_braquial,
            perimetro_cefalico=followup_data.perimetro_cefalico,
            pliegue_cutaneo=followup_data.pliegue_cutaneo,
            perimetro_abdominal=followup_data.perimetro_abdominal
        )
        db.add(datos_antropo)
        
        # Crear examen
        if followup_data.hemoglobina is not None:
            examen = Examen(
                seguimiento_id=nuevo_seguimiento.id_seguimiento,
                hemoglobina=followup_data.hemoglobina
            )
            db.add(examen)
        
        # **NUEVO: Realizar evaluación nutricional y guardarla**
        if followup_data.peso and followup_data.estatura:
            # Obtener datos del infante para calcular edad
            from src.db.models import Infante
            infante = db.query(Infante).filter(Infante.id_infante == followup_data.infante_id).first()
            
            if infante:
                # Calcular edad en días
                from datetime import datetime
                fecha_nacimiento = infante.fecha_nacimiento
                if isinstance(fecha_nacimiento, str):
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
                
                age_days = (followup_data.fecha - fecha_nacimiento).days
                gender = 'male' if infante.genero == 'M' else 'female'
                
                # Realizar evaluación nutricional
                assessment = NutritionService.assess_nutritional_status(
                    age_days=age_days,
                    weight=followup_data.peso,
                    height=followup_data.estatura,
                    gender=gender,
                    head_circumference=followup_data.perimetro_cefalico,
                    triceps_skinfold=followup_data.pliegue_cutaneo,
                    subscapular_skinfold=None
                )
                
                # Obtener requerimientos energéticos
                energy_req = NutritionService.get_energy_requirement(
                    age_days=age_days,
                    weight=followup_data.peso,
                    gender=gender,
                    feeding_mode='mixed',
                    activity_level='moderate'
                )
                
                # Obtener requerimientos de nutrientes
                nutrient_data = NutritionService.get_nutrient_food_table_data(
                    age_days=age_days,
                    gender=gender,
                    weight=followup_data.peso,
                    kcal_per_day=energy_req.get("kcal_per_day")
                )
                
                # Generar recomendaciones
                recommendations = NutritionService.generate_recommendations(assessment)
                
                # Guardar evaluación en la base de datos
                evaluacion = EvaluacionNutricional(
                    seguimiento_id=nuevo_seguimiento.id_seguimiento,
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
                    requerimientos_energeticos=energy_req,
                    requerimientos_nutrientes=nutrient_data,
                    recomendaciones_nutricionales=recommendations.get("nutritional_recommendations", []),
                    recomendaciones_generales=recommendations.get("general_recommendations", []),
                    instrucciones_cuidador=recommendations.get("caregiver_instructions", [])
                )
                db.add(evaluacion)
        
        db.commit()
        db.refresh(nuevo_seguimiento)
        
        return {
            "id_seguimiento": nuevo_seguimiento.id_seguimiento,
            "infante_id": nuevo_seguimiento.infante_id,
            "fecha": nuevo_seguimiento.fecha,
            "observacion": nuevo_seguimiento.observacion
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear seguimiento: {str(e)}")


@router.get("/")
def list_followups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todos los seguimientos con paginación
    """
    from src.db.models import Infante, DatoAntropometrico
    
    seguimientos = db.query(Seguimiento).order_by(Seguimiento.fecha.desc()).offset(skip).limit(limit).all()
    
    result = []
    for seg in seguimientos:
        # Obtener datos antropométricos
        datos_antropo = db.query(DatoAntropometrico).filter(
            DatoAntropometrico.seguimiento_id == seg.id_seguimiento
        ).first()
        
        # Obtener infante
        infante = db.query(Infante).filter(Infante.id_infante == seg.infante_id).first()
        
        result.append({
            "id_seguimiento": seg.id_seguimiento,
            "infante_id": seg.infante_id,
            "infante_nombre": infante.nombre if infante else None,
            "fecha": seg.fecha.isoformat() if seg.fecha else None,
            "observacion": seg.observacion,
            "peso": float(datos_antropo.peso) if datos_antropo and datos_antropo.peso else None,
            "estatura": float(datos_antropo.estatura) if datos_antropo and datos_antropo.estatura else None,
            "imc": float(datos_antropo.imc) if datos_antropo and datos_antropo.imc else None
        })
    
    return result


@router.get("/{seguimiento_id}/evaluacion")
def get_evaluacion_nutricional(seguimiento_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la evaluación nutricional completa de un seguimiento
    """
    evaluacion = db.query(EvaluacionNutricional).filter(
        EvaluacionNutricional.seguimiento_id == seguimiento_id
    ).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    return {
        "assessment": {
            "bmi": float(evaluacion.imc) if evaluacion.imc else None,
            "weight_for_age_zscore": float(evaluacion.peso_edad_zscore) if evaluacion.peso_edad_zscore else None,
            "height_for_age_zscore": float(evaluacion.talla_edad_zscore) if evaluacion.talla_edad_zscore else None,
            "bmi_for_age_zscore": float(evaluacion.imc_edad_zscore) if evaluacion.imc_edad_zscore else None,
            "head_circumference_zscore": float(evaluacion.perimetro_cefalico_zscore) if evaluacion.perimetro_cefalico_zscore else None,
            "triceps_skinfold_zscore": float(evaluacion.pliegue_triceps_zscore) if evaluacion.pliegue_triceps_zscore else None,
            "subscapular_skinfold_zscore": float(evaluacion.pliegue_subescapular_zscore) if evaluacion.pliegue_subescapular_zscore else None,
            "nutritional_status": {
                "peso_edad": evaluacion.clasificacion_peso_edad,
                "talla_edad": evaluacion.clasificacion_talla_edad,
                "peso_talla": evaluacion.clasificacion_peso_talla,
                "imc_edad": evaluacion.clasificacion_imc_edad,
                "perimetro_cefalico_edad": evaluacion.clasificacion_perimetro_cefalico,
                "pliegue_triceps": evaluacion.clasificacion_pliegue_triceps,
                "pliegue_subescapular": evaluacion.clasificacion_pliegue_subescapular
            },
            "risk_level": evaluacion.nivel_riesgo
        },
        "energy_requirements": evaluacion.requerimientos_energeticos,
        "nutrient_requirements": evaluacion.requerimientos_nutrientes,
        "recommendations": {
            "nutritional_recommendations": evaluacion.recomendaciones_nutricionales,
            "general_recommendations": evaluacion.recomendaciones_generales,
            "caregiver_instructions": evaluacion.instrucciones_cuidador
        }
    }


@router.get("/infante/{infante_id}/historial")
def get_historial_evaluaciones(infante_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el historial completo de evaluaciones de un infante
    para mostrar en el perfil y generar estadísticas
    """
    from sqlalchemy import desc
    
    evaluaciones = db.query(
        EvaluacionNutricional,
        Seguimiento,
        DatoAntropometrico
    ).join(
        Seguimiento, EvaluacionNutricional.seguimiento_id == Seguimiento.id_seguimiento
    ).join(
        DatoAntropometrico, Seguimiento.id_seguimiento == DatoAntropometrico.seguimiento_id
    ).filter(
        Seguimiento.infante_id == infante_id
    ).order_by(
        desc(Seguimiento.fecha)
    ).all()
    
    historial = []
    for eval, seg, datos in evaluaciones:
        historial.append({
            "id_seguimiento": seg.id_seguimiento,
            "fecha": seg.fecha,
            "nivel_riesgo": eval.nivel_riesgo,
            "peso": float(datos.peso) if datos.peso else None,
            "estatura": float(datos.estatura) if datos.estatura else None,
            "imc": float(eval.imc) if eval.imc else None,
            "clasificaciones": {
                "peso_edad": eval.clasificacion_peso_edad,
                "talla_edad": eval.clasificacion_talla_edad,
                "imc_edad": eval.clasificacion_imc_edad
            },
            "zscores": {
                "peso_edad": float(eval.peso_edad_zscore) if eval.peso_edad_zscore else None,
                "talla_edad": float(eval.talla_edad_zscore) if eval.talla_edad_zscore else None,
                "imc_edad": float(eval.imc_edad_zscore) if eval.imc_edad_zscore else None
            }
        })
    
    return historial


@router.get("/estadisticas/dashboard")
def get_estadisticas_dashboard(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas agregadas para el dashboard principal
    """
    from sqlalchemy import func, distinct
    
    # Total de infantes evaluados
    total_infantes = db.query(func.count(distinct(Seguimiento.infante_id))).scalar()
    
    # Distribución por nivel de riesgo
    distribucion_riesgo = db.query(
        EvaluacionNutricional.nivel_riesgo,
        func.count(distinct(Seguimiento.infante_id))
    ).join(
        Seguimiento, EvaluacionNutricional.seguimiento_id == Seguimiento.id_seguimiento
    ).group_by(
        EvaluacionNutricional.nivel_riesgo
    ).all()
    
    # Promedios de indicadores
    promedios = db.query(
        func.avg(EvaluacionNutricional.peso_edad_zscore).label('promedio_peso_edad'),
        func.avg(EvaluacionNutricional.talla_edad_zscore).label('promedio_talla_edad'),
        func.avg(EvaluacionNutricional.imc_edad_zscore).label('promedio_imc_edad')
    ).first()
    
    return {
        "total_infantes": total_infantes,
        "distribucion_riesgo": {nivel: count for nivel, count in distribucion_riesgo},
        "promedios_zscores": {
            "peso_edad": float(promedios.promedio_peso_edad) if promedios.promedio_peso_edad else 0,
            "talla_edad": float(promedios.promedio_talla_edad) if promedios.promedio_talla_edad else 0,
            "imc_edad": float(promedios.promedio_imc_edad) if promedios.promedio_imc_edad else 0
        }
    }