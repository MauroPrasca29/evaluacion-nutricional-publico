from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from src.services.nutrition_service import NutritionService
import tempfile
import datetime

router = APIRouter(tags=["nutrition"])

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
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"{name.replace(' ', '_')}_reporte_nutricional_{fecha}.pdf"

    return FileResponse(tmp_path, media_type="application/pdf", filename=nombre_archivo)


@router.get("/growth-chart-data", summary="Obtiene datos de curvas de crecimiento para graficar")
def get_growth_chart_data(
    indicator: str = Query(..., description="Indicador: peso, talla, imc, perimetro_cefalico, pliegue_triceps, pliegue_subescapular"),
    age_days: int = Query(..., description="Edad en días"),
    gender: str = Query(..., description="male/female"),
    value: float = Query(..., description="Valor del indicador")
):
    """
    Devuelve los datos de las curvas de crecimiento OMS en formato JSON
    para ser graficadas en el frontend con Recharts.
    """
    import math
    
    # Función para calcular percentiles sin scipy
    def calculate_percentile_value(L, M, S, percentile):
        """
        Calcula el valor del percentil usando la fórmula LMS de la OMS
        sin necesidad de scipy
        """
        # Convertir percentil a z-score aproximado
        # Aproximación de la función inversa de distribución normal
        p = percentile / 100.0
        
        # Aproximación de Beasley-Springer-Moro para la función inversa
        if p == 0.5:
            z = 0
        elif p < 0.5:
            t = math.sqrt(-2 * math.log(p))
            z = -t + (2.515517 + 0.802853*t + 0.010328*t*t) / (1 + 1.432788*t + 0.189269*t*t + 0.001308*t*t*t)
        else:
            t = math.sqrt(-2 * math.log(1-p))
            z = t - (2.515517 + 0.802853*t + 0.010328*t*t) / (1 + 1.432788*t + 0.189269*t*t + 0.001308*t*t*t)
        
        # Calcular valor usando fórmula LMS
        try:
            if L != 0:
                value = M * math.pow(1 + L * S * z, 1 / L)
            else:
                value = M * math.exp(S * z)
            return value
        except:
            return M  # Fallback a la mediana si hay error
    
    # Mapeo de nombres en español a nombres en inglés
    indicator_map = {
        "peso": "weight",
        "talla": "height",
        "imc": "bmi",
        "perimetro_cefalico": "head_circumference",
        "pliegue_triceps": "triceps_skinfold",
        "pliegue_subescapular": "subscapular_skinfold"
    }
    
    # Convertir indicador si está en español
    indicator_en = indicator_map.get(indicator.lower(), indicator)
    
    # Obtener tabla del indicador
    indicator_table = NutritionService.get_table_for_indicator(indicator_en, gender, age_days)
    if indicator_table is None or indicator_table.empty:
        raise HTTPException(status_code=404, detail=f"No se encontró tabla para el indicador {indicator}")
    
    # Obtener columna de edad
    age_col = NutritionService.get_age_column_name(indicator_table)
    ages = indicator_table[age_col].copy()
    
    # Convertir edades a meses si es necesario
    if "año" in age_col.lower():
        ages = ages * 12
    elif "day" in age_col.lower() or "dias" in age_col.lower():
        ages = ages / NutritionService.DAYS_PER_MONTH
    
    # Obtener valores LMS
    M = indicator_table['M']
    L = indicator_table['L']
    S = indicator_table['S']
    
    # Percentiles a calcular
    percentiles = [3, 15, 50, 85, 97]
    
    # Construir datos para la gráfica
    chart_data = []
    for i in range(len(ages)):
        data_point = {
            "age": float(ages.iloc[i])
        }
        
        # Calcular cada percentil
        for p in percentiles:
            percentile_value = calculate_percentile_value(
                L.iloc[i], 
                M.iloc[i], 
                S.iloc[i], 
                p
            )
            data_point[f'p{p}'] = round(float(percentile_value), 2)
        
        chart_data.append(data_point)
    
    # Reducir densidad de datos para mejorar rendimiento en frontend
    if len(chart_data) > 100:
        # Tomar puntos cada N posiciones para reducir a ~80 puntos
        step = len(chart_data) // 80
        chart_data = [chart_data[i] for i in range(0, len(chart_data), max(1, step))]
    
    # Calcular edad del niño en meses
    child_age_months = age_days / NutritionService.DAYS_PER_MONTH
    
    # Nombres de indicadores
    indicator_names = {
        "weight": "Peso (kg)",
        "height": "Estatura (cm)",
        "bmi": "IMC (kg/m²)",
        "head_circumference": "Perímetro cefálico (cm)",
        "triceps_skinfold": "Pliegue tricipital (mm)",
        "subscapular_skinfold": "Pliegue subescapular (mm)"
    }
    
    return {
        "indicator": indicator,
        "indicator_name": indicator_names.get(indicator_en, indicator_en),
        "gender": gender,
        "child_age_months": round(child_age_months, 1),
        "child_value": round(value, 2),
        "chart_data": chart_data
    }