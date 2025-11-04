from nutrition_service import NutritionService
from tabulate import tabulate

def test_nutricional_completo():
    # Datos del infante (todos los requeridos por la API)
    name = "Saray"
    age_days = 2555          # ≈ 2 años
    weight = 12.8            # kg
    height = 87.0            # cm
    gender = "male"
    head_circumference = 49.0
    triceps_skinfold = 9.5
    subscapular_skinfold = 7.5
    activity_level = "vigorous"
    feeding_mode = "breast"  # Nuevo campo requerido

    # 1. Evaluación antropométrica
    assessment = NutritionService.assess_nutritional_status(
        age_days, weight, height, gender,
        head_circumference, triceps_skinfold, subscapular_skinfold
    )

    # 2. Requerimientos energéticos para cada modo de alimentación
    print("\nREQUERIMIENTOS ENERGÉTICOS")
    print("-" * 50)
    feeding_modes = ["breast", "formula", "mixed"]
    energia_tabla = []
    energia_dict = {}
    for mode in feeding_modes:
        req = NutritionService.get_energy_requirement(
            age_days=age_days,
            weight=weight,
            gender=gender,
            feeding_mode=mode,
            activity_level=activity_level
        )
        energia_tabla.append([
            mode,
            req['kcal_per_kg_str'],
            req['kcal_per_day_str'],
            req.get('row_label', 'No especificado'),
            req.get('used_column', 'No especificada')
        ])
        energia_dict[mode] = req

    print(tabulate(
        energia_tabla,
        headers=["Modo alimentación", "Kcal/kg/día", "Kcal/día", "Rango edad", "Columna usada"],
        tablefmt="grid"
    ))

    # 3. Generar recomendaciones
    recommendations = NutritionService.generate_recommendations(assessment)

    # 4. Datos del infante para el reporte (incluye feeding_mode y name)
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

    # 5. Generar reporte PDF
    NutritionService.export_report_pdf(
        "reporte_nutricional.pdf",
        assessment,
        age_days,
        gender,
        recommendations,
        child_data
    )
    print("\nReporte PDF generado: reporte_nutricional.pdf")

if __name__ == "__main__":
    print("Ejecutando test nutricional completo...")
    test_nutricional_completo()