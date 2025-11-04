# Nutritional assessment service
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class NutritionService:

    # Cargar tablas
    @staticmethod
    def get_table(variable: str, gender: str) -> pd.DataFrame:
        files = {
            "weight": {
                "male": "backend/data/who_tables/Peso-Niños- de 0 a 5 años.xlsx",
                "female": "backend/data/who_tables/Peso-Niñas- de 0 a 5 años.xlsx"
            },
            "height": {
                "male": "backend/data/who_tables/Estatura-Niños- de 0 a 5 años.xlsx",
                "female": "backend/data/who_tables/Estatura-Niñas- de 0 a 5 años.xlsx"
            },
            "bmi": {
                "male": "backend/data/who_tables/IMC-Niños- de 0 a 5 años.xlsx",
                "female": "backend/data/who_tables/IMC-Niñas- de 0 a 5 años.xlsx"
            },
            "head_circumference": {
                "male": "backend/data/who_tables/Circunferencia craneal-Niños- de 0 a 5 años.xlsx",
                "female": "backend/data/who_tables/Circunferencia craneal-Niñas- de 0 a 5 años.xlsx"
            },
            "triceps_skinfold": {
                "male": "backend/data/who_tables/Pliegue cutaneo del triceps-Niños- de 0 a 5 años.xlsx",
                "female": "backend/data/who_tables/Pliegue cutaneo del triceps-Niñas- de 0 a 5 años.xlsx"
            },
            "subscapular_skinfold": {
                "male": "backend/data/who_tables/Pliegue cutáneo subescapular-Niños- de 0 a 5 años.xlsx",
                "female": "backend/data/who_tables/Pliegue cutáneo subescapular-Niñas- de 0 a 5 años.xlsx"
            }
        }
        return pd.read_excel(files[variable][gender])


    @staticmethod
    def get_lms_row(table: pd.DataFrame, day: int) -> Dict[str, float]:
        row = table[table["Day"] == day].iloc[0]
        return {"L": row["L"], "M": row["M"], "S": row["S"]}
    
    @staticmethod
    def calculate_zscore(measurement: float, L: float, M: float, S: float) -> float:
        if L == 0:
            return (measurement - M) / S
        else:
            return ((measurement / M) ** L - 1) / (L * S)
    
    @staticmethod
    def calculate_bmi(weight: float, height: float) -> float:
        """Calculate BMI"""
        height_m = height / 100  # Convert cm to meters
        return weight / (height_m ** 2)
    
    @staticmethod
    def assess_nutritional_status(
        age_days: int,
        weight: float,
        height: float,
        gender: str,
        head_circumference: float = None,
        triceps_skinfold: float = None,
        subscapular_skinfold: float = None
    ) -> Dict[str, Any]:
        bmi = NutritionService.calculate_bmi(weight, height)

        # Cargar tablas según sexo
        weight_table = NutritionService.get_table("weight", gender)
        height_table = NutritionService.get_table("height", gender)
        bmi_table = NutritionService.get_table("bmi", gender)
        hc_table = NutritionService.get_table("head_circumference", gender)
        tsf_table = NutritionService.get_table("triceps_skinfold", gender)
        ssf_table = NutritionService.get_table("subscapular_skinfold", gender)

        # Obtener parámetros LMS
        weight_lms = NutritionService.get_lms_row(weight_table, age_days)
        height_lms = NutritionService.get_lms_row(height_table, age_days)
        bmi_lms = NutritionService.get_lms_row(bmi_table, age_days)
        hc_lms = NutritionService.get_lms_row(hc_table, age_days) if head_circumference is not None else None
        tsf_lms = NutritionService.get_lms_row(tsf_table, age_days) if triceps_skinfold is not None else None
        ssf_lms = NutritionService.get_lms_row(ssf_table, age_days) if subscapular_skinfold is not None else None

        # Calcular z-scores
        weight_z = NutritionService.calculate_zscore(weight, weight_lms["L"], weight_lms["M"], weight_lms["S"])
        height_z = NutritionService.calculate_zscore(height, height_lms["L"], height_lms["M"], height_lms["S"])
        bmi_z = NutritionService.calculate_zscore(bmi, bmi_lms["L"], bmi_lms["M"], bmi_lms["S"])
        hc_z = NutritionService.calculate_zscore(head_circumference, hc_lms["L"], hc_lms["M"], hc_lms["S"]) if hc_lms else None
        tsf_z = NutritionService.calculate_zscore(triceps_skinfold, tsf_lms["L"], tsf_lms["M"], tsf_lms["S"]) if tsf_lms else None
        ssf_z = NutritionService.calculate_zscore(subscapular_skinfold, ssf_lms["L"], ssf_lms["M"], ssf_lms["S"]) if ssf_lms else None

        
        def classify(z):
            if z is None:
                return ""
            if z < -3:
                return "muy bajo"
            elif z < -2:
                return "bajo"
            elif z > 3:
                return "muy alto"
            elif z > 2:
                return "alto"
            else:
                return "normal"

        nutritional_status = {
            "peso": classify(weight_z),
            "talla": classify(height_z),
            "imc": classify(bmi_z),
            "circunferencia_craneal": classify(hc_z),
            "pliegue_triceps": classify(tsf_z),
            "pliegue_subescapular": classify(ssf_z)
        }

        
        # Lógica de riesgo bajo/medio/alto
        z_scores = [weight_z, height_z, bmi_z, hc_z, tsf_z, ssf_z]
        print("Z-scores:", z_scores)
        riesgo = "bajo"
        if any(z is not None and (z < -2 or z > 2) for z in z_scores):
            riesgo = "alto"
        elif any(z is not None and ((-2 <= z < -1.5) or (1.5 < z <= 2)) for z in z_scores):
            riesgo = "medio"

        risk_level = riesgo

        return {
            "bmi": bmi,
            "weight_for_age_zscore": weight_z,
            "height_for_age_zscore": height_z,
            "bmi_for_age_zscore": bmi_z,
            "head_circumference_zscore": hc_z,
            "triceps_skinfold_zscore": tsf_z,
            "subscapular_skinfold_zscore": ssf_z,
            "nutritional_status": nutritional_status,
            "risk_level": risk_level,
            "weight_lms": weight_lms,
            "height_lms": height_lms,
            "bmi_lms": bmi_lms
        }
    
    @staticmethod
    def generate_recommendations(assessment: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate nutritional recommendations"""
        # TODO: Implement recommendation logic based on assessment
        
        return {
            "nutritional_recommendations": [
                "Mantener alimentación balanceada",
                "Incluir frutas y verduras diariamente"
            ],
            "general_recommendations": [
                "Continuar con controles regulares",
                "Mantener higiene adecuada"
            ],
            "caregiver_instructions": [
                "Ofrecer comidas variadas",
                "Asegurar hidratación adecuada"
            ]
        }
