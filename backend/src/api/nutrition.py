from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from services.nutrition_service import NutritionService
import tempfile
import os

router = APIRouter(tags=["nutrition"])

@router.get("/nutritional-report")
def get_nutritional_report(
    name: str = Query("N/A"),
    age_days: int = Query(...),
    weight: float = Query(...),
    height: float = Query(...),
    gender: str = Query(...),
    head_circumference: float = Query(...),
    triceps_skinfold: float = Query(...),
    subscapular_skinfold: float = Query(...),
    activity_level: str = Query("moderate"),
    feeding_mode: str = Query("breast", description="Tipo de alimentación: breast, formula, mixed")
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
        "feeding_mode": feeding_mode

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