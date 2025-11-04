from nutrition_service import NutritionService
from tabulate import tabulate

age_days = 365      # 1 año
weight = 10.7       # kg 
height = 74.0       # cm 
gender = "male"
head_circumference = 44.0  # cm 
triceps_skinfold = 7.0     # mm 
subscapular_skinfold = 5.0 # mm 

assessment = NutritionService.assess_nutritional_status(
    age_days, weight, height, gender,
    head_circumference, triceps_skinfold, subscapular_skinfold
)

# Obtener rangos de referencia desde las tablas OMS
def get_reference_range(variable, gender, age_days):
    table = NutritionService.get_table(variable, gender)
    row = table[table["Day"] == age_days].iloc[0]
    min_normal = row["SD2neg"]  # z-score -2
    max_normal = row["SD2"]     # z-score +2
    return min_normal, max_normal

ranges = {
    "BMI": get_reference_range("bmi", gender, age_days),
    "Peso": get_reference_range("weight", gender, age_days),
    "Talla": get_reference_range("height", gender, age_days),
    "Circunferencia craneal": get_reference_range("head_circumference", gender, age_days),
    "Pliegue triceps": get_reference_range("triceps_skinfold", gender, age_days),
    "Pliegue subescapular": get_reference_range("subscapular_skinfold", gender, age_days),
}

# Mostrar tabla de resultados con rangos
table = [
    ["BMI", assessment["bmi"], assessment["nutritional_status"]["imc"], "-2 a 2"],
    ["Peso z-score", assessment["weight_for_age_zscore"], assessment["nutritional_status"]["peso"], "-2 a 2"],
    ["Talla z-score", assessment["height_for_age_zscore"], assessment["nutritional_status"]["talla"], "-2 a 2"],
    ["IMC z-score", assessment["bmi_for_age_zscore"], assessment["nutritional_status"]["imc"], "-2 a 2"],
    ["Circunferencia craneal z-score", assessment["head_circumference_zscore"], assessment["nutritional_status"]["circunferencia_craneal"], "-2 a 2"],
    ["Pliegue triceps z-score", assessment["triceps_skinfold_zscore"], assessment["nutritional_status"]["pliegue_triceps"], "-2 a 2"],
    ["Pliegue subescapular z-score", assessment["subscapular_skinfold_zscore"], assessment["nutritional_status"]["pliegue_subescapular"], "-2 a 2"],
    ["Riesgo", assessment["risk_level"], "", ""],
]

print(tabulate(table, headers=["Indicador", "Valor", "Estado", "Rango normal (z-score)"], tablefmt="grid"))

# Observación sobre valores en los límites
limite_superior = 1.8
limite_inferior = -1.8
observaciones = []
for nombre, z in [
    ("Peso", assessment["weight_for_age_zscore"]),
    ("Talla", assessment["height_for_age_zscore"]),
    ("IMC", assessment["bmi_for_age_zscore"]),
    ("Circunferencia craneal", assessment["head_circumference_zscore"]),
    ("Pliegue triceps", assessment["triceps_skinfold_zscore"]),
    ("Pliegue subescapular", assessment["subscapular_skinfold_zscore"])
]:
    if z is not None and (limite_inferior <= z < -1.5):
        observaciones.append(f"{nombre}: cerca del límite inferior, considerar subir el valor.")
    elif z is not None and (1.5 < z <= limite_superior):
        observaciones.append(f"{nombre}: cerca del límite superior, considerar bajar el valor.")

if not observaciones:
    observacion_general = "Todo está bien, todos los valores están dentro de los límites normales."
else:
    observacion_general = "Todo está bien, pero los siguientes valores están cerca de los límites y deben ser monitoreados:\n" + "\n".join(observaciones)

print("\nObservación:")
print(observacion_general)
# Generar recomendaciones
##recommendations = NutritionService.generate_recommendations(assessment)
##print("Recomendaciones:", recommendations)