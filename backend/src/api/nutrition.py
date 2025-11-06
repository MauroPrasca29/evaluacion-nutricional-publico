from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from src.services.nutrition_service import NutritionService
import tempfile
import os

router = APIRouter(prefix="/nutrition", tags=["nutrition"])

@router.get("/nutritional-report", response_class=FileResponse, summary="Genera y descarga un reporte nutricional en PDF")
def get_nutritional_report(
    name: str = Query("N/A"),
    age_days: int = Query(..., description="Edad en días"),
    weight: float = Query(..., description="Peso en kg"),
    height: float = Query(..., description="Estatura en cm"),
    gender: str = Query(..., description="male/female"),
    head_circumference: float = Query(..., description="Perímetro cefálico en cm"),
    triceps_skinfold: float = Query(..., description="Pliegue tricipital en mm"),
    subscapular_skinfold: float = Query(..., description="Pliegue subescapular en mm"),
    activity_level: str = Query("moderate", description="Nivel de actividad"),
    feeding_mode: str = Query("breast", description="Tipo de alimentación: breast, formula, mixed"),
    nutricionist_observation = Query(..., description="nutricionist_observation")
):
    assessment = NutritionService.assess_nutritional_status(
        age_days, weight, height, gender,
        head_circumference, triceps_skinfold, subscapular_skinfold
    )
    recommendations = NutritionService.generate_recommendations(assessment)
    child_data = {
        "name": name,
        "weight": weight,
        "height": height,
        "head_circumference": head_circumference,
        "triceps_skinfold": triceps_skinfold,
        "subscapular_skinfold": subscapular_skinfold,
        "activity_level": activity_level,
        "feeding_mode": feeding_mode,
        "nutricionist_observation": nutricionist_observation
    }
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        NutritionService.export_report_pdf(
            tmp.name,
            assessment,
            age_days,
            gender,
            recommendations,
            child_data
        )
        tmp_path = tmp.name
    return FileResponse(tmp_path, media_type="application/pdf", filename="reporte_nutricional.pdf")