"""Servicio de evaluación nutricional.
"""
import logging
import os
import re
import tempfile
import shutil
from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Logging básico (configurable desde la app)
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class NutritionService:

    # Configuration / constants
    CONFIG_DATA_DIR = Path(__file__).parent.parent.parent / "data"
    
    # time constants
    DAYS_PER_MONTH = 30.44
    DAYS_PER_YEAR = 365

    # energy densities (kcal per gram) - needed for calculations
    ENERGY_KCAL_PER_G_PROTEIN = 4.0
    ENERGY_KCAL_PER_G_CARBO = 4.0
    ENERGY_KCAL_PER_G_FAT = 9.0
    ENERGY_KCAL_PER_G_FIBER = 2.0

    # minimum values for validity checks
    MIN_VALOR_100G = 1e-6
    EPS_INT_COMPARE = 1e-9

    # zscore observation thresholds - needed for classifications
    ZSCORE_OBS_UPPER = 1.8
    ZSCORE_OBS_LOWER = -1.8

    NUTRIENTE_COL_MAP = {
        "HIERRO* mg/día": "Hierro (mg)",
        "ZINC mg/día": "Zinc (mg)",
        "YODO mg/día": "Yodo (mg)",
        "CALCIO mg/día": "Calcio (mg)",
        "FÓSFORO mg/día": "Fósforo (mg)",
        "MAGNESIO mg/día": "Magnesio (mg)",
        "SODIO mg/día": "Sodio (mg)",
        "POTASIO mg/día": "Potasio (mg)",
        "Ácidos Grasos Saturados": "Grasa Saturada (g)",
        "Histidina g/kg/día": "Histidina (g)",
        "Isoleucina g/kg/día": "Isoleucina (g)",
        "Leucina g/kg/día": "Leucina (g)",
        "Lisina g/kg/día": "Lisina (g)",
        "Metionina + Cisteína g/kg/día": ["Metionina (g)", "Cisteína (g)"],
        "Fenilalanina + Tirosina g/kg/día": ["Fenilalanina (g)", "Tirosina (g)"],
        "Treonina g/kg/día": "Treonina (g)",
        "Triptófano g/kg/día": "Triptófano (g)",
        "Valina g/kg/día": "Valina (g)",
        "Proteínas g/kg/día": "Proteína (g)",
        "Fibra g/día Aia": "Fibra Dietaria (g)",
        "Carbohidratos g/día": "Carbohidratos Totales (g)"
    }

    @staticmethod
    def get_table_for_indicator(variable: str, gender: str, age_days: int) -> pd.DataFrame:
        """
        Devuelve la tabla adecuada para el indicador (peso, talla, IMC, perímetro cefálico, pliegues)
        según la edad y el género.
        """
        age_years = age_days / NutritionService.DAYS_PER_YEAR
        files = {
            "weight": {
                "male": {
                    "0-5": "Peso-Niños- de 0 a 5 años.xlsx",
                    "5-10": "Peso-Niños- de 5 a 10 años.xlsx"
                },
                "female": {
                    "0-5": "Peso-Niñas- de 0 a 5 años.xlsx", 
                    "5-10": "Peso-niñas- de 0 a 5 años.xlsx"
                }
            },
            "height": {
                "male": {
                    "0-5": "Estatura-Niños- de 0 a 5 años.xlsx",
                    "5-10": "Estatura-Niños- de 5 a 19 años.xlsx"
                },
                "female": {
                    "0-5": "Estatura-Niñas- de 0 a 5 años.xlsx",
                    "5-10": "Estatura-Niñas- de 5 a 19 años.xlsx"  
                }
            },
            "bmi": {
                "male": {
                    "0-5": "IMC-Niños- de 0 a 5 años.xlsx",
                    "5-19": "IMC-Niños- de 5 a 19 años.xlsx"
                },
                "female": {
                    "0-5": "IMC-Niñas- de 0 a 5 años.xlsx",
                    "5-19": "IMC-Niñas- de 5 a 19 años.xlsx"
                }
            },
            "head_circumference": {
                "male": "Circunferencia craneal-Niños- de 0 a 5 años.xlsx",
                "female": "Circunferencia craneal-Niñas- de 0 a 5 años.xlsx"
            },
            "triceps_skinfold": {
                "male": "Pliegue cutaneo del triceps-Niños- de 0 a 5 años.xlsx",
                "female": "Pliegue cutaneo del triceps-Niñas- de 0 a 5 años.xlsx"
            },
            "subscapular_skinfold": {
                "male": "Pliegue cutáneo subescapular-Niños- de 0 a 5 años.xlsx",
                "female": "Pliegue cutáneo subescapular-Niñas- de 0 a 5 años.xlsx"
            }
        }
        # Selección según edad y variable
        if variable in ["weight", "height"]:
            if age_years <= 5:
                filename = files[variable][gender]["0-5"]
            else:
                filename = files[variable][gender]["5-10"]
        elif variable == "bmi":
            if age_years <= 5:
                filename = files[variable][gender]["0-5"]
            else:
                filename = files[variable][gender]["5-19"]
        elif variable in ["head_circumference", "triceps_skinfold", "subscapular_skinfold"]:
            filename = files[variable][gender]
        else:
            raise ValueError(f"Indicador '{variable}' no soportado en get_table_for_indicator.")
        ruta_tabla = NutritionService.CONFIG_DATA_DIR / "who_tables" / filename
        return NutritionService._safe_read_excel(str(ruta_tabla))


    @staticmethod
    def get_lms_row(table: "pd.DataFrame", day: int):
        """
        Devuelve la fila LMS correspondiente al 'day'.
        Estrategia:
        - intentar coincidencia exacta en columna 'Day' o primera columna,
        - intentar búsqueda por rangos tipo '1-2' en la columna 'Day' (si existe),
        - fallback: devolver la fila numéricamente más cercana.
        Lanza IndexError con mensaje claro si la tabla está vacía o no contiene valores numéricos.
        """

        if table is None or len(table) == 0:
            raise IndexError(f"LMS table vacía; no es posible buscar day={day}")

        # detectar columna de días
        day_col = None
        if "Day" in table.columns:
            day_col = "Day"
        else:
            # asumir primera columna como etiqueta de edad/día si no existe 'Day'
            day_col = table.columns[0]

        # preparar vector numérico intentando extraer número desde texto
        raw_days = table[day_col].astype(str).fillna("").astype(str)

        # 1) intento: coincidencia exacta numérica
        numeric = pd.to_numeric(raw_days.str.extract(r'(\d+)', expand=False), errors="coerce")
        if numeric.notna().any():
            mask_exact = numeric == int(day)
            if mask_exact.any():
                return table[mask_exact].iloc[0]

        # 2) intento: buscar rangos tipo "lo-hi" en la columna original
        try:
            for _, row in table.iterrows():
                text = str(row[day_col])
                m = re.search(r'(\d+)\s*[-–]\s*(\d+)', text)
                if m:
                    lo = int(m.group(1)); hi = int(m.group(2))
                    if lo <= int(day) <= hi:
                        return row
        except Exception:
            pass

        # 3) fallback: usar la fila con 'day' numérico más cercano (si hay valores numéricos)
        if numeric.notna().any():
            idx = (numeric - int(day)).abs().idxmin()
            return table.loc[idx]

        # 4) si no hay valores numéricos ni rangos, error informativo
        raise IndexError(f"No se pudo localizar fila LMS para day={day}. Columna '{day_col}' no contiene días numéricos ni rangos.")
    
    @staticmethod
    def calculate_zscore(measurement: float, L: float, M: float, S: float) -> float:
        if L == 0:
            return (measurement - M) / S
        else:
            return ((measurement / M) ** L - 1) / (L * S)
    
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
        """
        Evalúa el estado nutricional según la edad:
        - Menores de 5 años: todas las medidas antropométricas
        - 5-11 años: solo peso, talla e IMC
        - >11 años: no permitido
        """
        # Validar edad máxima (11 años)
        age_years = age_days / NutritionService.DAYS_PER_YEAR
        if age_years > 11:
            raise ValueError(f"La edad no puede ser mayor a 11 años (edad proporcionada: {age_years:.1f} años)")

        bmi = NutritionService.calculate_bmi(weight, height)

        # Cargar tablas básicas (peso, talla, IMC)
        weight_table = NutritionService.get_table_for_indicator("weight", gender, age_days)
        height_table = NutritionService.get_table_for_indicator("height", gender, age_days)
        bmi_table = NutritionService.get_table_for_indicator("bmi", gender, age_days)
        
        # Helper seguro para get_lms_row
        def _safe_lms(tbl, day):
            try:
                return NutritionService.get_lms_row(tbl, day)
            except Exception:
                return None

        # Helper para validar LMS
        def _valid_lms(x):
            return x if (x is not None and not getattr(x, "empty", False)) else None

        # Obtener LMS para medidas básicas
        weight_lms = _valid_lms(_safe_lms(weight_table, age_days))
        height_lms = _valid_lms(_safe_lms(height_table, age_days))
        bmi_lms = _valid_lms(_safe_lms(bmi_table, age_days))

        # Helper cálculo z seguro
        def _calc_if(measure, lms):
            if measure is None or lms is None:
                return None
            try:
                return NutritionService.calculate_zscore(measure, lms["L"], lms["M"], lms["S"])
            except Exception:
                return None

        # Calcular z-scores básicos
        weight_z = _calc_if(weight, weight_lms)
        height_z = _calc_if(height, height_lms)
        bmi_z = _calc_if(bmi, bmi_lms)

        # Para menores de 5 años, incluir medidas adicionales
        hc_z = tsf_z = ssf_z = None
        if age_years <= 5:
            if head_circumference is not None:
                hc_table = NutritionService.get_table_for_indicator("head_circumference", gender, age_days)
                hc_lms = _valid_lms(_safe_lms(hc_table, age_days))
                hc_z = _calc_if(head_circumference, hc_lms)
                
            if triceps_skinfold is not None:
                tsf_table = NutritionService.get_table_for_indicator("triceps_skinfold", gender, age_days)
                tsf_lms = _valid_lms(_safe_lms(tsf_table, age_days))
                tsf_z = _calc_if(triceps_skinfold, tsf_lms)
                
            if subscapular_skinfold is not None:
                ssf_table = NutritionService.get_table_for_indicator("subscapular_skinfold", gender, age_days)                
                ssf_lms = _valid_lms(_safe_lms(ssf_table, age_days))
                ssf_z = _calc_if(subscapular_skinfold, ssf_lms)
                

        # Clasificaciones
        def classify_pt(z):
            if z is None:
                return ""
            if z > 3:
                return "Obesidad"
            elif 2 < z <= 3:
                return "Sobrepeso"
            elif 1 < z <= 2:
                return "Riesgo de Sobrepeso"
            elif -1 <= z <= 1:
                return "Peso Adecuado para la Talla"
            elif -2 <= z < -1:
                return "Riesgo de Desnutrición Aguda"
            elif -3 <= z < -2:
                return "Desnutrición Aguda Moderada"
            elif z < -3:
                return "Desnutrición Aguda Severa"
            return ""

        def classify_te(z):
            if z is None:
                return ""
            if z >= -1:
                return "Talla Adecuada para la Edad"
            elif -2 <= z < -1:
                return "Riesgo de Talla Baja"
            elif z < -2:
                return "Talla Baja para la Edad o Retraso en Talla"
            return ""

        def classify_pe(z):
            if z is None:
                return ""
            if -1 <= z <= 1:
                return "Peso Adecuado para la Edad"
            elif -2 <= z < -1:
                return "Riesgo de Desnutrición Global"
            elif z < -2:
                return "Desnutrición Global"
            return ""

        def classify_default(z):
            if z is None:
                return ""
            if z < -3:
                return "Muy bajo"
            elif z < -2:
                return "Bajo"
            elif z < -1:
                return "Riesgo bajo"
            elif z <= 1:
                return "Normal"
            elif z <= 2:
                return "Riesgo alto"
            elif z <= 3:
                return "Alto"
            else:
                return "Muy alto"

        # Estado nutricional
        nutritional_status = {
            "peso_edad": classify_pe(weight_z),
            "talla_edad": classify_te(height_z),
            "peso_talla": classify_pt(bmi_z),
            "imc_edad": classify_default(bmi_z)
        }

        # Agregar clasificaciones adicionales solo para menores de 5 años
        if age_years <= 5:
            if hc_z is not None:
                nutritional_status["perimetro_cefalico_edad"] = classify_default(hc_z)
            if tsf_z is not None:
                nutritional_status["pliegue_triceps"] = classify_default(tsf_z)
            if ssf_z is not None:
                nutritional_status["pliegue_subescapular"] = classify_default(ssf_z)

        # Evaluar nivel de riesgo usando solo los indicadores disponibles según edad
        z_scores = [weight_z, height_z, bmi_z]
        if age_years <= 5:
            z_scores.extend([hc_z, tsf_z, ssf_z])

        risk_level = "Bajo"
        if any(z is not None and (z < -2 or z > 2) for z in z_scores):
            risk_level = "Alto"
        elif any(z is not None and ((-2 <= z < -1.5) or (1.5 < z <= 2)) for z in z_scores):
            risk_level = "Medio"

        return {
            "bmi": bmi,
            "weight_for_age_zscore": weight_z,
            "height_for_age_zscore": height_z,
            "bmi_for_age_zscore": bmi_z,
            "head_circumference_zscore": hc_z if age_years <= 5 else None,
            "triceps_skinfold_zscore": tsf_z if age_years <= 5 else None,
            "subscapular_skinfold_zscore": ssf_z if age_years <= 5 else None,
            "nutritional_status": nutritional_status,
            "risk_level": risk_level
        }
    
    @staticmethod
    def calculate_bmi(weight: Optional[float], height: Optional[float]) -> Optional[float]:
        """
        Calcula BMI = weight (kg) / (height (m))^2.
        Devuelve None si falta weight o height o si height == 0.
        """
        try:
            if weight is None or height is None:
                return None
            h_m = float(height) / 100.0
            if h_m <= 0:
                return None
            bmi = float(weight) / (h_m * h_m)
            return round(bmi, 2)
        except Exception:
            return None
    
    @staticmethod
    def get_rien_row(age_days: int, gender: str, is_pregnant=False, is_lactating=False) -> pd.Series:
        ruta_rien = NutritionService.CONFIG_DATA_DIR / "food_composition" / "Recomendaciones de Ingesta de Energía y Nutrientes (RIEN).xlsx"
        rien_df = NutritionService._safe_read_excel(str(ruta_rien), header=2)

        if age_days is None or rien_df is None or rien_df.empty:
            print("RIEN: DataFrame vacío o edad no válida")
            return None

        age_months = age_days / NutritionService.DAYS_PER_MONTH
        age_years = age_days / NutritionService.DAYS_PER_YEAR
        print(f"RIEN: age_days={age_days}, age_months={age_months:.2f}, age_years={age_years:.2f}, gender={gender}")

        first_col = rien_df.columns[0]

        def find_by_token(tokens: List[str]):
            for tok in tokens:
                mask = rien_df[first_col].astype(str).str.contains(tok, case=False, na=False)
                if mask.any():
                    print(f"RIEN: Token '{tok}' encontrado en fila: {rien_df[mask].iloc[0][first_col]}")
                    return rien_df[mask].iloc[0]
            return None

        # búsqueda por edad en meses para lactantes
        if age_months < 7:
            print("RIEN: Buscando rango lactantes 0-6 meses")
            row = find_by_token(["0-6", "0 - 6", "0 a 6"])
            if row is not None:
                print("RIEN: Fila seleccionada (lactantes 0-6):", row[first_col])
                return row
        if 7 <= age_months < 12:
            print("RIEN: Buscando rango lactantes 7-11 meses")
            row = find_by_token(["7-11", "7 - 11", "7 a 11"])
            if row is not None:
                print("RIEN: Fila seleccionada (lactantes 7-11):", row[first_col])
                return row

        # 1-3 años y 4-8 años
        if age_months >= 12 and age_months < 48:
            print("RIEN: Buscando rango 1-3 años")
            row = find_by_token(["1-3", "1 - 3", "1 a 3"])
            if row is not None:
                print("RIEN: Fila seleccionada (1-3 años):", row[first_col])
                return row
        if age_months >= 48 and age_months < 108:
            print("RIEN: Buscando rango 4-8 años")
            row = find_by_token(["4-8", "4 - 8", "4 a 8"])
            if row is not None:
                print("RIEN: Fila seleccionada (4-8 años):", row[first_col])
                return row

        # mayores y adolescentes: buscar por rangos numéricos en la columna (ej. '9-13', '14-18', ...)
        if age_months >= 108:
            print("RIEN: Buscando bloque por género y rango para mayores de 9 años")
            mujeres_idx = None
            for idx, r in rien_df.iterrows():
                text = str(r[first_col]).strip().lower()
                if "mujeres" in text:
                    mujeres_idx = idx
                    print(f"RIEN: Índice de inicio de bloque Mujeres (años): {mujeres_idx}")
                    break

            if gender not in ["male", "female"]:
                print(f"RIEN: Advertencia - género recibido '{gender}' no es 'male' ni 'female'")

            if gender == "male":
                search_range = range(0, mujeres_idx if mujeres_idx is not None else len(rien_df))
            else:
                search_range = range(mujeres_idx + 1 if mujeres_idx is not None else 0, len(rien_df))

            for idx in search_range:
                r = rien_df.iloc[idx]
                text = str(r[first_col]).strip().lower()
                m = re.search(r'(\d+)\s*[-–]\s*(\d+)', text)
                if m:
                    lo = float(m.group(1)); hi = float(m.group(2))
                    # Solo considerar rangos de años >= 9
                    if lo < 9:
                        continue
                    print(f"RIEN: Evaluando fila idx={idx}, texto='{text}', rango={lo}-{hi}")
                    if lo <= age_years <= hi:
                        print(f"RIEN: Fila seleccionada (mayores): {r[first_col]}")
                        return r
                m2 = re.search(r'>\s*(\d+)', text)
                if m2:
                    lo = float(m2.group(1))
                    if lo < 9:
                        continue
                    print(f"RIEN: Evaluando fila idx={idx}, texto='{text}', rango >{lo}")
                    if age_years > lo:
                        print(f"RIEN: Fila seleccionada (mayores): {r[first_col]}")
                        return r

            print("RIEN: No se encontró fila para mayores de 9 años en el bloque correcto")
            return None

        # gestación / lactancia: buscar por palabras clave
        if is_pregnant:
            print("RIEN: Buscando fila de gestación")
            row = find_by_token(["gesta", "embarazo", "gestación", "embaraz"])
            if row is not None:
                print("RIEN: Fila seleccionada (gestación):", row[first_col])
                return row
        if is_lactating:
            print("RIEN: Buscando fila de lactancia")
            row = find_by_token(["lactan", "lactancia", "lactante"])
            if row is not None:
                print("RIEN: Fila seleccionada (lactancia):", row[first_col])
                return row

        print("RIEN: No se encontró ninguna fila para la edad/género especificados")
        return None

    @staticmethod
    def _get_kcal_per_day_from_rien(rien_row: "pd.Series", weight: Optional[float] = None, age_days: Optional[int] = None):
        """
        Extrae kcal_per_day desde una fila RIEN de forma robusta.
        Intenta columnas con 'kcal'/'energ' primero, luego busca valores plausibles (200-4000 kcal).
        Si no encuentra y se provee weight, intenta usar get_energy_requirement.
        Retorna (kcal_per_day: Optional[float], used_col_key: Optional[str])
        """
        kcal_per_day = None
        kcal_col_guess = None
        try:
            kcal_cols = [c for c in list(rien_row.index) if ("energ" in str(c).lower() or "kcal" in str(c).lower() or "energia" in str(c).lower())]
            if kcal_cols:
                val = pd.to_numeric(rien_row[kcal_cols[0]], errors="coerce")
                if not pd.isna(val):
                    kcal_per_day = float(val)
                    kcal_col_guess = kcal_cols[0]
        except Exception:
            kcal_per_day = None

        if kcal_per_day is None:
            try:
                for k in rien_row.index:
                    try:
                        v = pd.to_numeric(rien_row[k], errors="coerce")
                        if not pd.isna(v):
                            vv = float(v)
                            if NutritionService.RANGO_KCAL_VALID[0] <= vv <= NutritionService.RANGO_KCAL_VALID[1]:
                                kcal_per_day = vv
                                kcal_col_guess = k
                                break
                    except Exception:
                        continue
            except Exception:
                pass

        if kcal_per_day is None and weight is not None:
            try:
                # Prefer using a real age_days when available; avoid calling with None
                req = None
                try:
                    req = NutritionService.get_energy_requirement(age_days=age_days, weight=weight, gender=None,
                                                                  feeding_mode="breast", activity_level=None)
                    source_info = "computed_from_get_energy_requirement_with_age" if age_days is not None else "computed_from_get_energy_requirement_no_age"
                except Exception:
                    # last resort: call with None if initial attempt fails
                    try:
                        req = NutritionService.get_energy_requirement(age_days=None, weight=weight, gender=None,
                                                                      feeding_mode="breast", activity_level=None)
                        source_info = "computed_from_get_energy_requirement_no_age"
                    except Exception:
                        req = None
                        source_info = None

                if req and req.get("kcal_per_day"):
                    kcal_per_day = req["kcal_per_day"]
                    kcal_col_guess = source_info or "computed_from_get_energy_requirement"
                    logger.info("_get_kcal_per_day_from_rien: kcal_per_day computed via get_energy_requirement (source=%s)", kcal_col_guess)
            except Exception:
                # do not raise; just leave kcal_per_day as None
                logger.debug("_get_kcal_per_day_from_rien: fallback get_energy_requirement failed")

        return kcal_per_day, kcal_col_guess
        

    @staticmethod
    def generate_recommendations(assessment: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate nutritional recommendations based on assessment and local food composition"""

        # Extraer datos relevantes del infante
        risk_level = assessment.get("risk_level")
        nutritional_status = assessment.get("nutritional_status")


        # Recomendaciones generales según estado nutricional
        recommendations = []
        if risk_level == "Alto" or "Muy bajo" in nutritional_status.values() or "Bajo" in nutritional_status.values():
            recommendations.append("Priorizar alimentos ricos en energía y proteínas como huevo, pescado, carne, leguminosas y cereales.")
            recommendations.append("Aumentar la frecuencia de comidas y ofrecer refrigerios nutritivos.")
        elif risk_level == "Medio":
            recommendations.append("Mantener una alimentación variada y equilibrada, vigilando el crecimiento.")
        else:
            recommendations.append("Mantener alimentación balanceada con alimentos locales disponibles.")

        # 8. Recomendaciones generales y para el cuidador
        general_recommendations = [
            "Continuar con controles regulares de crecimiento y desarrollo.",
            "Mantener higiene adecuada en la preparación de alimentos.",
            "Asegurar hidratación adecuada."
        ]
        caregiver_instructions = [
            "Ofrecer comidas variadas y adaptadas a la edad.",
            "Evitar alimentos ultraprocesados y bebidas azucaradas.",
            "Fomentar el consumo de frutas y verduras locales."
        ]

        return {
            "nutritional_recommendations": recommendations,
            "general_recommendations": general_recommendations,
            "caregiver_instructions": caregiver_instructions
        }
    
    @staticmethod
    def get_zscore_observations(assessment: dict) -> str:
        """
        Genera observaciones sobre los z-score de los indicadores antropométricos.
        """
        limite_superior = NutritionService.ZSCORE_OBS_UPPER
        limite_inferior = NutritionService.ZSCORE_OBS_LOWER
        observaciones = []
        zscores = [
            ("Peso", assessment.get("weight_for_age_zscore")),
            ("Talla", assessment.get("height_for_age_zscore")),
            ("IMC", assessment.get("bmi_for_age_zscore")),
            ("Circunferencia craneal", assessment.get("head_circumference_zscore")),
            ("Pliegue triceps", assessment.get("triceps_skinfold_zscore")),
            ("Pliegue subescapular", assessment.get("subscapular_skinfold_zscore"))
        ]
        for nombre, z in zscores:
            if z is not None and (limite_inferior <= z < -1.5):
                observaciones.append(f"{nombre}: cerca del límite inferior, considerar subir el valor.")
            elif z is not None and (1.5 < z <= limite_superior):
                observaciones.append(f"{nombre}: cerca del límite superior, considerar bajar el valor.")

        if not observaciones:
            return "Todo está bien, todos los valores están dentro de los límites normales."
        else:
            return "Todo está bien, pero los siguientes valores están cerca de los límites y deben ser monitoreados:\n" + "\n".join(observaciones)
        

    @staticmethod
    def get_age_column_name(df: "pd.DataFrame") -> str:
        # Busca la columna que representa la edad
        for col in df.columns:
            if col.lower() in ["day", "dias", "edad (dias)", "edad (meses)", "mes", "month", "edad (años)", "año"]:
                return col
            if "edad" in col.lower() or "mes" in col.lower() or "month" in col.lower() or "año" in col.lower():
                return col
        # Fallback: primera columna
        return df.columns[0]
    

    @staticmethod
    def plot_indicator_curve(indicator_table, age_days, value, indicator_name, gender, output_path):
        # Convierte días a meses
        try:
            import matplotlib.pyplot as plt
        except Exception:
            logger.warning("matplotlib no disponible: no se generarán curvas para %s", indicator_name)
            return

        age_col = NutritionService.get_age_column_name(indicator_table)
        ages_months = indicator_table[age_col]
        infante_months = age_days / NutritionService.DAYS_PER_MONTH
        # Si la columna está en años, conviértela a meses
        if "año" in age_col.lower():
            ages_months = ages_months * 12
        elif "day" in age_col.lower() or "dias" in age_col.lower():
            ages_months = ages_months / NutritionService.DAYS_PER_MONTH
        M = indicator_table['M']
        plt.figure(figsize=(6,4))
        plt.plot(ages_months, M, label=f'Media OMS ({indicator_name})')
        plt.scatter([infante_months], [value], color='red', label='Infante')        
        plt.xlabel('Edad (meses)')
        plt.ylabel(indicator_name)
        plt.title(f'{indicator_name} para la Edad')
        plt.legend(fontsize=6)
        plt.grid(True)  # Agrega cuadrículas
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def export_report_pdf(filename: str, assessment: dict, age_days: int, gender: str, recommendations: dict, child_data: dict):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        # Título
        story.append(Paragraph("Reporte de Evaluación Nutricional", styles['Title']))
        story.append(Spacer(1, 12))
        age_year = age_days / NutritionService.DAYS_PER_YEAR

        datos = [
            f"<b>Nombre:</b> {child_data.get('name', 'N/A')}",
            f"<b>Edad:</b> {age_year}",
            f"<b>Género:</b> {gender.capitalize()}",
            f"<b>Peso (kg):</b> {child_data.get('weight', 'N/A')}",
            f"<b>Estatura (cm):</b> {child_data.get('height', 'N/A')}",
            f"<b>IMC:</b> {assessment.get('bmi', 'N/A'):.2f}",
            f"<b>Circunferencia cefálica (cm):</b> {child_data.get('head_circumference', 'N/A')}",
            f"<b>Pliegue tricipital (mm):</b> {child_data.get('triceps_skinfold', 'N/A')}",
            f"<b>Pliegue subescapular (mm):</b> {child_data.get('subscapular_skinfold', 'N/A')}",
            f"<b>Nivel de actividad:</b> {child_data.get('activity_level', 'N/A')}",


        ]
        for d in datos:
            story.append(Paragraph(d, styles["Normal"]))
        story.append(Spacer(1, 12))

        # Calcular edad en años para filtrar indicadores
        age_years = age_days / NutritionService.DAYS_PER_YEAR

        # Tabla de indicadores y estado nutricional
        col_widths = [110, 90, 120, 120]

        header = [
            Paragraph("Indicador (Z-score)", styles["Heading4"]),
            Paragraph("Valor", styles["Heading4"]),
            Paragraph("Rango de referencia (normal)", styles["Heading4"]),
            Paragraph("Estado", styles["Heading4"]),
        ]

        table_data = [header]

        indicadores_basicos = [
            ("Peso para la Edad", assessment.get("weight_for_age_zscore", ""), "-1 ≤ z ≤ +1", assessment["nutritional_status"].get("peso_edad", "")),
            ("Talla para la Edad", assessment.get("height_for_age_zscore", ""), "-1 ≤ z ≤ +1", assessment["nutritional_status"].get("talla_edad", "")),
            ("IMC para la Edad", assessment.get("bmi_for_age_zscore", ""), "-1 ≤ z ≤ +1", assessment["nutritional_status"].get("imc_edad", "")),
        ]

        # Agregar indicadores básicos
        for indicador, valor, rango, estado in indicadores_basicos:
            row = [
                Paragraph(str(indicador), styles["Normal"]),
                Paragraph(str(valor), styles["Normal"]),
                Paragraph(str(rango), styles["Normal"]),
                Paragraph(str(estado), styles["Normal"]),
            ]
            table_data.append(row)

        # Agregar indicadores adicionales solo si edad <= 5 años
        if age_years <= 5:
            indicadores_adicionales = [
                ("Circunferencia craneal", assessment.get("head_circumference_zscore", ""), "-2 ≤ z ≤ +2", assessment["nutritional_status"].get("perimetro_cefalico_edad", "")),
                ("Pliegue triceps", assessment.get("triceps_skinfold_zscore", ""), "-1 ≤ z ≤ +1", assessment["nutritional_status"].get("pliegue_triceps", "")),
                ("Pliegue subescapular", assessment.get("subscapular_skinfold_zscore", ""), "-1 ≤ z ≤ +1", assessment["nutritional_status"].get("pliegue_subescapular", "")),
            ]
            for indicador, valor, rango, estado in indicadores_adicionales:
                row = [
                    Paragraph(str(indicador), styles["Normal"]),
                    Paragraph(str(valor), styles["Normal"]),
                    Paragraph(str(rango), styles["Normal"]),
                    Paragraph(str(estado), styles["Normal"]),
                ]
                table_data.append(row)


        COLOR_HEADER = colors.HexColor("#474876")
        COLOR_BORDER = colors.HexColor("#474876")

        table_style = TableStyle([
            # Fondo de encabezado
            ('BACKGROUND', (0,0), (-1,0), COLOR_HEADER),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            # Bordes externos gruesos
            ('BOX', (0,0), (-1,-1), 2.5, COLOR_BORDER),
            # Bordes internos delgados
            ('INNERGRID', (0,0), (-1,-1), 0.7, COLOR_BORDER),
            # Bordes entre nutrientes (por ejemplo, columna 0 y 1)
            ('LINEBEFORE', (1,0), (1,-1), 2, COLOR_BORDER),  # entre columna 0 y 1
            # Puedes agregar más líneas gruesas entre otras columnas si lo deseas
            # Ejemplo: ('LINEBEFORE', (2,0), (2,-1), 2, COLOR_BORDER),
            # Centrado y padding
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ])

        t_indicadores = Table(table_data, colWidths=col_widths)
        t_indicadores.setStyle(table_style)
   

        story.append(Paragraph("Indicadores y Estado Nutricional", styles['Heading2']))
        story.append(t_indicadores)
        risk = assessment.get('risk_level', '')
        note_text = f"<i>Riesgo: El infante posee un nivel de riesgo </i> {risk}"
        story.append(Spacer(1, 6))
        story.append(Paragraph(note_text, styles["Normal"]))
        story.append(Spacer(1, 12))


        
        # Observaciones
        obs = NutritionService.get_zscore_observations(assessment)
        story.append(Paragraph("Observación", styles['Heading2']))
        story.append(Paragraph(obs, styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Spacer(1, 12))
        story.append(PageBreak())

    
        # Gráficas de indicadores (solo básicas)
        # Peso
        weight_table = NutritionService.get_table_for_indicator("weight", gender, age_days)
        NutritionService.plot_indicator_curve(weight_table, age_days, child_data.get('weight', 0), "Peso", gender, "peso_curve.png")
        story.append(Paragraph("<b>Curva de Peso para la Edad</b>", styles["Heading2"]))
        story.append(Image("peso_curve.png", width=400, height=250))
        story.append(Spacer(1, 12))

        # Talla
        height_table = NutritionService.get_table_for_indicator("height", gender, age_days)
        NutritionService.plot_indicator_curve(height_table, age_days, child_data.get('height', 0), "Estatura", gender, "talla_curve.png")
        story.append(Paragraph("<b>Curva de Estatura para la Edad</b>", styles["Heading2"]))
        story.append(Image("talla_curve.png", width=400, height=250))
        story.append(Spacer(1, 12))
        story.append(PageBreak())

        # IMC
        bmi_table = NutritionService.get_table_for_indicator("bmi", gender, age_days)
        NutritionService.plot_indicator_curve(bmi_table, age_days, assessment["bmi"], "IMC", gender, "imc_curve.png")
        story.append(Paragraph("<b>Curva de IMC para la Edad</b>", styles["Heading2"]))
        story.append(Image("imc_curve.png", width=400, height=250))
        story.append(Spacer(1, 12))


        # Solo agregar gráficas adicionales si edad <= 5 años
        if age_years <= 5:
            
            # Perímetro cefálico
            hc_table = NutritionService.get_table_for_indicator("head_circumference", gender, age_days)
            NutritionService.plot_indicator_curve(hc_table, age_days, child_data.get('head_circumference', 0), 
                                                "Perímetro cefálico", gender, "hc_curve.png")
            story.append(Paragraph("<b>Curva de Perímetro cefálico para la Edad</b>", styles["Heading2"]))
            story.append(Image("hc_curve.png", width=400, height=250))
            story.append(Spacer(1, 12))
            story.append(PageBreak())

            
            # Pliegue tricipital
            tsf_table = NutritionService.get_table_for_indicator("triceps_skinfold", gender, age_days)
            NutritionService.plot_indicator_curve(tsf_table, age_days, child_data.get('triceps_skinfold', 0),
                                                "Pliegue tricipital", gender, "tsf_curve.png")
            story.append(Paragraph("<b>Curva de Pliegue tricipital para la Edad</b>", styles["Heading2"]))
            story.append(Image("tsf_curve.png", width=400, height=250))
            story.append(Spacer(1, 12))
            
            # Pliegue subescapular
            ssf_table = NutritionService.get_table_for_indicator("subscapular_skinfold", gender, age_days)
            NutritionService.plot_indicator_curve(ssf_table, age_days, child_data.get('subscapular_skinfold', 0),
                                                "Pliegue subescapular", gender, "ssf_curve.png")
            story.append(Paragraph("<b>Curva de Pliegue subescapular para la Edad</b>", styles["Heading2"]))
            story.append(Image("ssf_curve.png", width=400, height=250))
            story.append(Spacer(1, 12))
            
            
        
        story.append(PageBreak())
        story.append(Paragraph("<b>Requerimientos Energéticos</b>", styles["Heading2"]))

        # Obtener requerimientos con peso actual
        activity_level = child_data.get("activity_level")  # Si no está, usa "moderate"

        current_req = NutritionService.get_energy_requirement(
            age_days=age_days, 
            weight=child_data["weight"], 
            gender=gender,
            feeding_mode=child_data.get("feeding_mode", "breast"), 
            activity_level=activity_level
        )
        if current_req is None:
            current_req = {
                'kcal_per_kg_str': "No disponible",
                'kcal_per_day_str': "No disponible"
            }
                
        # Obtener peso esperado para la edad de las tablas WHO
        weight_table = NutritionService.get_table_for_indicator("weight", gender, age_days)
        weight_lms = NutritionService.get_lms_row(weight_table, age_days)
        expected_weight = weight_lms["M"] if weight_lms is not None else child_data["weight"]  # <-- Fallback al peso actual

        # Calcula kcal_per_day usando el peso esperado (o actual si no hay esperado)
        expected_req = NutritionService.get_energy_requirement(
            age_days=age_days, 
            weight=expected_weight, 
            gender=gender,
            feeding_mode=child_data.get("feeding_mode", "breast"),  
            activity_level=child_data.get("activity_level")
        )
        kcal_per_day = expected_req["kcal_per_day"] if expected_req and expected_req.get("kcal_per_day") else None

        nutrient_table = NutritionService.get_nutrient_food_table_data(
            age_days, gender, weight=expected_weight, kcal_per_day=kcal_per_day
        )

        # Lista de aminoácidos esenciales
        aminoacidos_escenciales = [
            "Histidina g/kg/día",
            "Isoleucina g/kg/día",
            "Leucina g/kg/día",
            "Lisina g/kg/día",
            "Metionina + Cisteína g/kg/día",
            "Fenilalanina + Tirosina g/kg/día",
            "Treonina g/kg/día",
            "Triptófano g/kg/día",
            "Valina g/kg/día"
        ]

        # Filtra la tabla de nutrientes si edad >= 9 años
        if age_years >= 9:
            nutrient_table = [item for item in nutrient_table if item.get("nutriente") not in aminoacidos_escenciales]

        print("Nutrientes en tabla final:", [item.get("nutriente") for item in nutrient_table])

        # Construye requerimientos_dict usando los valores recomendados de la tabla
        requerimientos_dict = {}
        for item in nutrient_table:
            nombre = item.get("nutriente")
            valor = item.get("valor_recomendado_g")
            if valor is not None:
                requerimientos_dict[nombre] = valor
        
        # Crear tabla de requerimientos energéticos
        energy_data = [
            ["", "Con peso actual", "Con peso esperado"],
            ["Peso (kg)", f"{child_data['weight']:.1f}", 
            f"{expected_weight:.1f}" if expected_weight is not None else "No disponible"],
            ["Energía por kg/día", 
            current_req['kcal_per_kg_str'] if current_req and 'kcal_per_kg_str' in current_req else "No disponible",
            expected_req['kcal_per_kg_str'] if expected_req and 'kcal_per_kg_str' in expected_req else "No disponible"],
            ["Energía total/día", 
            current_req['kcal_per_day_str'] if current_req and 'kcal_per_day_str' in current_req else "No disponible",
            expected_req['kcal_per_day_str'] if expected_req and 'kcal_per_day_str' in expected_req else "No disponible"]
        ]
            
        # Estilo para la tabla de requerimientos
        energy_table = Table(energy_data, colWidths=[120, 100, 100])
        energy_table.setStyle(table_style)
            
        story.append(energy_table)
        story.append(Spacer(1, 12))
            
        # Agregar nota explicativa
        if child_data['weight'] < expected_weight:
            diff_percent = ((expected_weight - child_data['weight']) / expected_weight) * 100
            note = f"<i>Nota: El peso actual está {diff_percent:.1f}% por debajo del peso esperado para la edad.</i>"
        else:
            diff_percent = ((child_data['weight'] - expected_weight) / expected_weight) * 100
            note = f"<i>Nota: El peso actual está {diff_percent:.1f}% por encima del peso esperado para la edad.</i>"
                
        story.append(Paragraph(note, styles["Normal"]))



        # Tabla detallada de requerimientos y alimentos
        # Obtén la tabla como lista de listas (no como string)
        # Estilo para encabezados en negrita y centrados
        header_style = ParagraphStyle(
            name='HeaderStyle',
            parent=styles['Normal'],
            alignment=1,  # 1 = center
            fontName='Helvetica-Bold',
            textColor='white'
        )

        # Encabezado de la tabla
        header = [
            Paragraph("Nutriente", header_style),
            Paragraph("Cantidad recomendada del nutriente", header_style),
            Paragraph("Alimento", header_style),
            Paragraph("Cantidad del nutriente en cada 100g del alimento", header_style),
            Paragraph("Cantidad recomendada del alimento (g/día)", header_style)
        ]
        table_data = [header]
        # nutrient_table entries are structured dicts produced by get_nutrient_food_table_data

        for item in nutrient_table:
            alimentos = item.get("alimentos") or []
            num_alimentos = max(1, len(alimentos))
            filas = alimentos if alimentos else [["No disponible", "", ""]]
            for idx, alimento in enumerate(filas):
                # alimento can be legacy list [name, display_per_100, cantidad_str] or dict from helpers
                if isinstance(alimento, dict):
                    nombre = alimento.get('nombre')
                    if 'valor_100g' in alimento:
                        valor_100g = alimento.get('valor_100g')
                    else:
                        valor_100g = alimento.get('valor_100g_sum')
                    unidad_100g = alimento.get('unidad_100g') or alimento.get('unidad') or 'g'
                    cantidad_recomendada = alimento.get('cantidad_recomendada_g') if alimento.get('cantidad_recomendada_g') is not None else ''
                    display_valor_100 = f"{NutritionService.format_number(valor_100g,3)} g" if valor_100g not in (None, '') else ""
                else:
                    # legacy list format
                    nombre = alimento[0] if len(alimento) > 0 else 'No disponible'
                    display_valor_100 = alimento[1] if len(alimento) > 1 else ''
                    cantidad_recomendada = alimento[2] if len(alimento) > 2 else ''
                
                if item.get('nutriente') == "Ácidos Grasos Saturados" and item.get('valor_recomendado_unit') == "<g":
                    valor_recomendado_str = item.get('valor_recomendado')
                else:
                    valor_recomendado_str = f"{item.get('valor_recomendado_g'):.5f} g" if item.get('valor_recomendado_g') is not None else ""
                
                # Build the row: include nutrient name and recommendation only on the first alimento row
                if idx == 0:
                    # --- MODIFICACIÓN PARA GRASA POLIINSATURADA ---
                    
                    if item.get('nutriente') == "Grasa Poliinsaturada (g)" and item.get('amdr_details'):
                        g_lo = item['amdr_details']['g_lo']
                        g_hi = item['amdr_details']['g_hi']
                        pct_lo = item['amdr_details']['pct_lo']
                        pct_hi = item['amdr_details']['pct_hi']
                        kcal = item['amdr_details']['kcal_per_day']
                        valor_recomendado_str = f"{g_lo:.1f}-{g_hi:.1f} g ({pct_lo:.1f}-{pct_hi:.1f}% de {kcal:.0f} kcal)"
                    else:
                        valor_recomendado_str = f"{item.get('valor_recomendado_g'):.5f} g" if item.get('valor_recomendado_g') is not None else ""

                    row = [
                        Paragraph(str(item.get('nutriente') or ''), styles['Normal']),
                        Paragraph(valor_recomendado_str, styles['Normal']),
                        Paragraph(str(nombre or ''), styles['Normal']),
                        Paragraph(str(display_valor_100), styles['Normal']),
                        Paragraph(str(cantidad_recomendada), styles['Normal'])
                    ]
                else:
                    row = [
                        Paragraph('', styles['Normal']),
                        Paragraph('', styles['Normal']),
                        Paragraph(str(nombre or ''), styles['Normal']),
                        Paragraph(str(display_valor_100), styles['Normal']),
                        Paragraph(str(cantidad_recomendada), styles['Normal'])
                    ]
                table_data.append(row)




        t = Table(table_data, colWidths=[90, 80, 120, 90, 90])
        
        t.setStyle(table_style)
        

        # Aplica rowSpan como antes...
        nutrient_row_indices = []
        row_idx = 1
        for item in nutrient_table:
            nutrient_row_indices.append(row_idx)
            num_alimentos = max(1, len(item["alimentos"]))
            if num_alimentos > 1:
                t.setStyle(TableStyle([
                    ('SPAN', (0, row_idx), (0, row_idx + num_alimentos - 1)),
                    ('SPAN', (1, row_idx), (1, row_idx + num_alimentos - 1)),
                ]))
            row_idx += num_alimentos
        for row_idx in nutrient_row_indices:
            t.setStyle(TableStyle([
                ('LINEABOVE', (0, row_idx), (-1, row_idx), 2, COLOR_BORDER)
            ]))
        
        story.append(Paragraph("Requerimientos diarios de energía y nutrientes para el infante", styles['Heading2']))
        story.append(t)
        story.append(Spacer(1, 12))
        story.append(PageBreak())

        # Recomendaciones nutricionales
        story.append(Paragraph("Recomendaciones nutricionales", styles['Heading2']))
        for key, recs in recommendations.items():
            story.append(Paragraph(key.replace('_', ' ').capitalize(), styles['Heading3']))
            for rec in recs:
                story.append(Paragraph(f"- {rec}", styles['Normal']))
            story.append(Spacer(1, 6))

        ruta_alimentos = NutritionService.CONFIG_DATA_DIR / "food_composition" / "alimentos_cartagena_completo.xlsx"
        alimentos_df = NutritionService._safe_read_excel(str(ruta_alimentos))
        print(alimentos_df.columns)
                
        """""        
        platos = NutritionService.generar_platos_saludables_multi(nutrient_table, requerimientos_dict, alimentos_df)
        story.append(Paragraph("<b>Opciones de platos saludables sugeridos</b>", styles["Heading2"]))
        for i, plato in enumerate(platos, 1):
            story.append(Paragraph(f"Opción {i}:", styles["Heading3"]))
            for item in plato:
                story.append(Paragraph(
                    f"{item['alimento']} ({item['grupo']}): {item['cantidad_g']} g", styles["Normal"]
                ))
            story.append(Spacer(1, 6))
        story.append(PageBreak())


        nutrientes_evaluados = list(requerimientos_dict.keys())

        for i, plato in enumerate(platos, 1):
            story.append(Paragraph(f"<b>Composición nutricional de la opción {i}</b>", styles["Heading3"]))
            # Encabezado de la tabla
            header = [Paragraph("Alimento", styles["Heading4"])] + [Paragraph(n, styles["Heading4"]) for n in nutrientes_evaluados]
            tabla_composicion = [header]
            # Filas por alimento
            totales = {n: 0.0 for n in nutrientes_evaluados}
            for item in plato:
                fila = [Paragraph(item["alimento"], styles["Normal"])]
                alimento_row = alimentos_df[alimentos_df["Nombre Corregido"] == item["alimento"]].iloc[0]
                for nutriente in nutrientes_evaluados:
                    col_map = NutritionService.NUTRIENTE_COL_MAP.get(nutriente)
                    if isinstance(col_map, list):
                        valor_100g = sum(alimento_row[c] if c in alimento_row else 0 for c in col_map)
                    else:
                        valor_100g = alimento_row[col_map] if col_map in alimento_row else 0
                    aporte = valor_100g * item["cantidad_g"] / 100 if valor_100g and item["cantidad_g"] else 0
                    totales[nutriente] += aporte
                    # Mostrar 0 si el aporte es cero
                    fila.append(Paragraph(f"{NutritionService.format_number(aporte,2) if aporte else '0'}", styles["Normal"]))
                tabla_composicion.append(fila)
            # Fila de totales
            fila_total = [Paragraph("<b>Total</b>", styles["Normal"])] + [Paragraph(f"<b>{NutritionService.format_number(totales[n],2)}</b>", styles["Normal"]) for n in nutrientes_evaluados]
            tabla_composicion.append(fila_total)
            # Mostrar tabla
            t_comp = Table(tabla_composicion, colWidths=[90] + [60]*len(nutrientes_evaluados))
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(t_comp)
            story.append(Spacer(1, 12))
            """""

        doc.build(story)

    @staticmethod
    def amdr_range_to_grams(kcal_per_day: float, amdr_value: str, nutrient_name: Optional[str] = None):
        """
        Convierte un string AMDR tipo "5-10" o "5-10%" a un rango de gramos/día según kcal_per_day.
        Usa densidades energéticas:
        - proteínas: 4 kcal/g
        - carbohidratos: 4 kcal/g
        - grasas: 9 kcal/g
        - fibra: 2 kcal/g
        Para vitaminas/minerales devuelve g_lo/g_hi = None (no aplicable).
        Retorna (display_str, details_dict)
        details_dict = { 'pct_lo','pct_hi','kcal_lo','kcal_hi','g_lo','g_hi','energy_per_g' }
        """
        if kcal_per_day is None or amdr_value is None:
            return None, None

        s = str(amdr_value).strip()
        # limpiar unidades residuales (ej. "g/día" que a veces aparece)
        s_clean = re.sub(r'(g\/día|g/day|g/d|g)', '', s, flags=re.IGNORECASE).strip()

        m = re.match(r'^\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*%?\s*$', s_clean)
        m_lt = re.match(r'^\s*<\s*(\d+(?:\.\d+)?)\s*%?\s*$', s_clean)
        m_single = re.match(r'^\s*(\d+(?:\.\d+)?)\s*%?\s*$', s_clean)

        if m:
            pct_lo = float(m.group(1)); pct_hi = float(m.group(2))
        elif m_lt:
            pct_lo = 0.0; pct_hi = float(m_lt.group(1))
        elif m_single:
            pct_lo = pct_hi = float(m_single.group(1))
        else:
            return None, None

        # detectar tipo de nutriente para energy_per_g
        epg = None
        if nutrient_name:
            nk = nutrient_name.lower()
            if "prote" in nk:          # proteína(s)
                epg = NutritionService.ENERGY_KCAL_PER_G_PROTEIN
            elif "carbo" in nk or "glúcido" in nk or "gluc" in nk:
                epg = NutritionService.ENERGY_KCAL_PER_G_CARBO
            elif "grasa" in nk or "ácidos grasos" in nk or "poliinsaturado" in nk or "saturado" in nk:
                epg = NutritionService.ENERGY_KCAL_PER_G_FAT
            elif "lipid" in nk or "lípido" in nk:
                epg = NutritionService.ENERGY_KCAL_PER_G_FAT
            elif "fibra" in nk:
                epg = NutritionService.ENERGY_KCAL_PER_G_FIBER
            # minerales/vitaminas/agua -> epg permanece None

        kcal_lo = kcal_per_day * (pct_lo / 100.0)
        kcal_hi = kcal_per_day * (pct_hi / 100.0)

        if epg is None:
            # no convertible a gramos por energía (p. ej. minerales/vitaminas)
            details = {
                'pct_lo': pct_lo, 'pct_hi': pct_hi,
                'kcal_lo': kcal_lo, 'kcal_hi': kcal_hi,
                'g_lo': None, 'g_hi': None,
                'energy_per_g': None
            }
            display = f"{pct_lo:.1f}-{pct_hi:.1f}% de {kcal_per_day:.0f} kcal"
            return display, details

        # conversión a gramos
        g_lo = kcal_lo / epg
        g_hi = kcal_hi / epg

        display = f"{g_lo:.1f}-{g_hi:.1f} g ({pct_lo:.1f}-{pct_hi:.1f}% de {kcal_per_day:.0f} kcal)"
        details = {
            'pct_lo': pct_lo, 'pct_hi': pct_hi,
            'kcal_lo': kcal_lo, 'kcal_hi': kcal_hi,
            'g_lo': g_lo, 'g_hi': g_hi,
            'energy_per_g': epg
        }
        return display, details
        

    @staticmethod
    def _parse_rien_value(raw_val, unidad_hint, kcal_per_day=None, nutriente=None, weight=None):
        """
        Parse a RIEN cell value into a canonical tuple.

        Returns: (display_str, value_grams: Optional[float], unit: Optional[str], amdr_details: Optional[dict])
        """
        if raw_val is None:
            return None, None, None, None

        amdr_details = None
        s = str(raw_val).strip()

        # --- AMDR with "<" symbol, e.g. "<10" or "<10%" ---
        if isinstance(raw_val, str) and raw_val.strip().startswith("<"):
            # Si no tiene %, agrégalo
            if "%" not in raw_val:
                s = raw_val + "%"
            m = re.search(r"<\s*([0-9]+(?:\.[0-9]+)?)\s*%", s)
            if m and kcal_per_day:
                pct = float(m.group(1))
                kcal = pct * kcal_per_day / 100.0
                gramos = kcal / 9.0
                display = f"<{gramos:.2f} g (<{pct}% de {kcal_per_day:.0f} kcal)"
                return display, gramos, "<g", {"pct": pct, "kcal": kcal, "gramos": gramos, "symbol": "<"}

        # --- AMDR percent ranges like "10-35%" or single percent "25%" ---
        if "%" in s:
            try:
                amdr_res = NutritionService.amdr_range_to_grams(kcal_per_day, s, nutrient_name=nutriente)
                if amdr_res is None:
                    return s, None, "%", None
                display, details = amdr_res
                g_lo = details.get('g_lo')
                g_hi = details.get('g_hi')
                value_g = None
                if g_lo is not None and g_hi is not None:
                    try:
                        value_g = float((g_lo + g_hi) / 2.0)
                    except Exception:
                        value_g = None
                return display, value_g, "%", details
            except Exception:
                return s, None, "%", None

        # --- Compound values like "A + B" ---
        if "+" in s:
            parts = [p.strip() for p in s.split("+")]
            total_g = 0.0
            any_numeric = False
            details_parts = []
            for p in parts:
                disp, val_g, unit_p, amdr_p = NutritionService._parse_rien_value(p, unidad_hint, kcal_per_day=kcal_per_day, nutriente=nutriente)
                details_parts.append({'text': disp, 'g': val_g, 'unit': unit_p, 'amdr': amdr_p})
                if val_g is not None:
                    any_numeric = True
                    total_g += float(val_g)
            display = " + ".join([d['text'] for d in details_parts])
            if any_numeric:
                return display, float(total_g), unidad_hint or 'g', None
            else:
                return display, None, unidad_hint or None, None

        # --- Numeric values with explicit units (mg, ug, g) ---
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(mg|μg|ug|g)\b", s, flags=re.I)
        if m:
            try:
                v = float(m.group(1))
                u = m.group(2).lower()
                if u in ("μg", "ug"):
                    grams = v / 1_000_000.0
                    return s, grams, 'mcg', None
                if u == 'mg':
                    grams = v / 1000.0
                    return s, grams, 'mg', None
                if u == 'g':
                    return s, v, 'g', None
            except Exception:
                return s, None, None, None

        # --- Plain numeric interpreted as grams (or use unidad_hint to interpret differently) ---
        pnum = re.findall(r"[0-9]+(?:\.[0-9]+)?", s)
        if pnum:
            v = float(pnum[0])
            uk = str(unidad_hint).lower() if unidad_hint else ""
            if nutriente:
                n = nutriente.lower()
                # Lista de nutrientes que deben multiplicarse por el peso
                aa_list = [
                    "proteína", "histidina", "isoleucina", "leucina", "lisina",
                    "metionina", "cisteína", "metionina + cisteína",
                    "fenilalanina", "tirosina", "fenilalanina + tirosina",
                    "treonina", "triptófano", "valina"
                ]
                if any(aa in n for aa in aa_list):
                    if uk in ("g/kg/día", "g/kg"):
                        if weight is not None:
                            return s, v * weight, 'g', None
                        else:
                            return s, v, 'g', None
                    else:
                        return s, v, 'g', None
                # Carbohidratos y fibra: tomar el valor directamente en gramos
                if "carbohidrato" in n or "fibra" in n:
                    return s, v, 'g', None
            # Otros nutrientes: convertir según unidad
            if uk in ('mg', 'mg/día', 'mg/dia'):
                return s, v / 1000.0, 'mg', None
            if uk in ('mcg', 'μg', 'ug', 'mcg/día'):
                return s, v / 1_000_000.0, 'mcg', None
            if uk in ('g', 'g/día', 'g/dia'):
                return s, v, 'g', None

        return None, None, None, None
        
    @staticmethod
    def _build_alimentos_for_nutrient(foods_df, col_name, valor_recomendado_g, amdr_details=None, top_n=5):
        """Return a list of top foods for a single nutrient column.

        Each item: {"nombre": name, "valor_100g": val, "valor_por_porcion_g": val_portion}
        """
        if col_name not in foods_df.columns:
            return []
        # convert using centralized per-column converter to grams per 100
        serie_grams = NutritionService._convert_series_to_grams(foods_df[col_name], col_name)
        mask_valid = serie_grams.notna() & (serie_grams > NutritionService.MIN_VALOR_100G)
        df_valid = foods_df.loc[mask_valid].copy()
        if df_valid.empty:
            return []
        df_valid = df_valid.assign(_valor_100g=serie_grams.loc[df_valid.index])
        df_valid = df_valid.sort_values("_valor_100g", ascending=False)
        top = df_valid.head(top_n)
        result = []
        for idx, row in top.iterrows():
            try:
                name = row.get('Nombre Corregido') or row.get('Nombre') or str(idx)
            except Exception:
                name = str(idx)
            val = float(row.get('_valor_100g') or 0.0)
            result.append({"nombre": name, "valor_100g": val, "unidad_100g": "g"})
        return result

    @staticmethod
    def _build_alimentos_for_combination(foods_df, cols, valor_recomendado_g, amdr_details=None, top_n=5, fill_missing_with_zero: bool = False):
        """Return top foods for a combination of nutrient columns (sum of specified cols).

        cols: list of column names to sum. This function tolerates missing columns: if
        `fill_missing_with_zero` is True, missing numeric parts will be treated as 0
        for scoring purposes (but original data is left untouched). At least one
        part must be significant (> MIN_VALOR_100G) for a food to be considered.
        """
        # keep the order of provided cols but only keep those that exist or can be faked
        existing = [c for c in cols if c in foods_df.columns]
        if not existing:
            return []

        # For each existing column compute grams per 100g series
        parts = []
        for c in existing:
            parts.append(NutritionService._convert_series_to_grams(foods_df[c], c))

        # Build DataFrame with parts as columns
        parts_df = pd.DataFrame({f"part_{i}": parts[i] for i in range(len(parts))}, index=foods_df.index)

        # If allowed, fill missing values with 0 to tolerate absent values
        if fill_missing_with_zero:
            parts_df_f = parts_df.fillna(0.0)
        else:
            parts_df_f = parts_df

        # mask: require at least one part > MIN_VALOR_100G
        mask_significant = (parts_df_f > NutritionService.MIN_VALOR_100G).any(axis=1)
        # also remove rows that are entirely NaN when not filling
        if not fill_missing_with_zero:
            mask_not_all_na = parts_df.notna().any(axis=1)
            mask_valid = mask_significant & mask_not_all_na
        else:
            mask_valid = mask_significant

        df_valid = foods_df.loc[mask_valid].copy()
        if df_valid.empty:
            return []

        # attach numeric parts (use parts_df_f which may have zeros)
        for i, c in enumerate(existing):
            df_valid[f"valor_100g_part_{i}"] = parts_df_f.loc[df_valid.index, f"part_{i}"]

        df_valid["sum_parts"] = df_valid[[f"valor_100g_part_{i}" for i in range(len(existing))]].sum(axis=1)
        df_valid = df_valid.sort_values("sum_parts", ascending=False)

        result = []
        for idx, row in df_valid.head(top_n).iterrows():
            try:
                name = row.get('Nombre Corregido') or row.get('Nombre') or str(idx)
            except Exception:
                name = str(idx)
            per100 = {existing[i]: float(row.get(f"valor_100g_part_{i}") or 0.0) for i in range(len(existing))}
            result.append({"nombre": name, "valor_100g_sum": float(row.get('sum_parts') or 0.0), "detalle_por_100g": per100, "unidad": "g"})
        return result


    @staticmethod
    def format_number(value: Optional[float], max_decimals: int = 2) -> str:
        """
        Devuelve:
         - entero sin decimales si value es entero (o muy cercano a entero),
         - o string con hasta max_decimals decimales, sin ceros a la derecha innecesarios.
        """
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        try:
            v = float(value)
        except Exception:
            return str(value)
        # considerar entero si la diferencia es insignificante
        if abs(v - round(v)) < NutritionService.EPS_INT_COMPARE:
            return str(int(round(v)))
        s = f"{v:.{max_decimals}f}"
        # quitar ceros y punto sobrante
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s
    
    @staticmethod
    def _infer_col_unit(col_name: Optional[str]) -> Optional[str]:
        """Inferir unidad a partir del nombre de columna: 'g','mg','mcg','%' o None."""
        if not col_name:
            return None
        s = str(col_name).lower()
        if any(x in s for x in ("mcg", "µg", "μg", "ug")):
            return "mcg"
        if "mg" in s and "mg/" not in s:  # detectar mg
            return "mg"
        if "g" in s or any(tok in s for tok in ("proteína", "proteina", "lipid", "grasa", "carbohidr", "fibra")):
            return "g"
        if "%" in s:
            return "%"
        return None

    @staticmethod
    def _to_grams_per_100(value: Any, unit: Optional[str], column_max: Optional[float] = None) -> Optional[float]:
        """
        Convertir un valor numérico (seguro) de la unidad indicada a gramos por 100g.
        unit: 'g'|'mg'|'mcg'|'%'|None
        Usa heurística por column_max si unit es None.
        """
        try:
            if value is None:
                return None
            v = float(value)
        except Exception:
            return None

        if unit == "mg":
            return v / 1000.0
        if unit == "mcg":
            return v / 1_000_000.0
        if unit == "g":
            return v
        # porcentaje o no convertible -> no convertir a gramos
        if unit == "%":
            return None
        # fallback heurística: si la columna tiene máximos altos -> tratar como mg
        try:
            if column_max is not None and float(column_max) > NutritionService.LARGE_VALUE_THRESHOLD:
                return v / 1000.0
        except Exception:
            pass
        # si el valor en sí es grande -> probablemente está en mg
        if v > NutritionService.LARGE_VALUE_THRESHOLD:
            return v / 1000.0
        return v

    @staticmethod
    def _convert_series_to_grams(series: "pd.Series", col_name: Optional[str]) -> "pd.Series":
        """
        Convertir una serie (posiblemente con strings) a gramos por 100g.
        Devuelve pd.Series(float) con NaN donde no convertible.
        """
        colnum = pd.to_numeric(series, errors="coerce")
        col_max = float(colnum.max()) if colnum.notna().any() else None
        unit = NutritionService._infer_col_unit(col_name)
        return colnum.apply(lambda v: NutritionService._to_grams_per_100(v, unit, col_max))

    @staticmethod
    def _find_food_col(foods_df: "pd.DataFrame", expected: Optional[str]) -> Optional[str]:
        """
        Búsqueda tolerante de una columna en `foods_df` dada una etiqueta esperada.

        Estrategia (en orden):
         1. Normalizar (quitar acentos, paréntesis, unidades y caracteres no alfanuméricos) y comparar exacta/insensible a mayúsculas.
         2. Buscar coincidencia por token completo (palabra) en los nombres normalizados de columnas.
         3. Intentar coincidencias parciales por fragmentos de palabras (prioriza palabras largas).
         4. Fallback: devolver None (el llamador puede decidir usar alternativas o marcar "No disponible").

        Esta función no lanza; captura excepciones internamente y devuelve None si no hay coincidencias.
        """
        if expected is None:
            return None

        import unicodedata

        def _strip_accents(s: str) -> str:
            nk = unicodedata.normalize('NFKD', s)
            return ''.join(ch for ch in nk if not unicodedata.combining(ch))

        def _normalize_name(s: Any) -> str:
            if s is None:
                return ''
            t = str(s)
            t = _strip_accents(t)
            t = t.lower()
            # remove parenthesis content and common unit tokens
            t = re.sub(r'\(.*?\)', ' ', t)
            t = re.sub(r'\b(mcg|ug|μg|mg|g|kcal|kj|%)\b', ' ', t)
            t = re.sub(r'[^a-z0-9\s]', ' ', t)
            t = re.sub(r'\s+', ' ', t).strip()
            return t

        try:
            norm_expected = _normalize_name(expected)
            # build normalized column map once
            cols = list(foods_df.columns)
            norm_map = {c: _normalize_name(c) for c in cols}

            # 1) exact normalized match
            for c, nc in norm_map.items():
                if nc == norm_expected and nc:
                    return c

            # 2) exact token match (split expected into tokens)
            tokens = [t for t in norm_expected.split() if t]
            if tokens:
                for token in tokens:
                    # prefer longer tokens first
                    for c, nc in sorted(norm_map.items(), key=lambda x: -len(x[1])):
                        if token and token in nc:
                            return c

            # 3) fallback: try first-word match against original column names (lenient)
            first = str(expected).strip().split()[0].lower()
            if first:
                for c in cols:
                    if first in str(c).lower():
                        return c
        except Exception:
            return None

        return None

    @staticmethod
    def get_nutrient_food_table_data(age_days: int, gender: str, weight: Optional[float] = None, kcal_per_day: Optional[float] = None):

        debug = False  # poner True para prints de depuración

        nutriente_col_map = {
            "HIERRO* mg/día": "RDA",
            "ZINC mg/día": "RDA.1",
            "YODO mg/día": "RDA.2",
            "CALCIO mg/día": "RDA.5",
            "FÓSFORO mg/día": "RDA.6",
            "MAGNESIO mg/día": "RDA.7",
            "SODIO mg/día": "AI.9",
            "POTASIO mg/día": "AI.10",
            "Ácidos Grasos Poliinsaturados n-6 (ácido linoleico)": "AMDR%.1",
            "Ácidos Grasos Poliinsaturados n-3 (ácido alfa linolénico)": "AMDR%.2",
            "Ácidos Grasos Saturados": "AMDR%.3",
            "Colesterol": "AMDR%.6",
            "Histidina g/kg/día": "RDA.8",
            "Isoleucina g/kg/día": "RDA.9",
            "Leucina g/kg/día": "RDA.10",
            "Lisina g/kg/día": "RDA.11",
            "Metionina + Cisteína g/kg/día": "RDA.12",
            "Fenilalanina + Tirosina g/kg/día": "RDA.13",
            "Treonina g/kg/día": "RDA.14",
            "Triptófano g/kg/día": "RDA.15",
            "Valina g/kg/día": "RDA.16",
            "Proteínas g/kg/día": "RDA.17",
            "Fibra g/día Aia": "AI.30",
            "Carbohidratos g/día": "RDA.18",
        }
        nutriente_alimentos_map = {
            "HIERRO* mg/día": "Hierro (mg)",
            "ZINC mg/día": "Zinc (mg)",
            "YODO mg/día": "Yodo (mg)",
            "CALCIO mg/día": "Calcio (mg)",
            "FÓSFORO mg/día": "Fósforo (mg)",
            "MAGNESIO mg/día": "Magnesio (mg)",
            "SODIO mg/día": "Sodio (mg)",
            "POTASIO mg/día": "Potasio (mg)",
            "Ácidos Grasos Poliinsaturados n-6 (ácido linoleico)": "Grasa Poliinsaturada (g)",
            "Ácidos Grasos Poliinsaturados n-3 (ácido alfa linolénico)": "Grasa Poliinsaturada (g)",
            "Ácidos Grasos Saturados": "Grasa Saturada (g)",
            "Ácidos Grasos Monoinsaturados": "Grasa Monoinsaturada (g)",
            "Colesterol": "Colesterol (mg)",
            "Histidina g/kg/día": "Histidina (g)",
            "Isoleucina g/kg/día": "Isoleucina (g)",
            "Leucina g/kg/día": "Leucina (g)",
            "Lisina g/kg/día": "Lisina (g)",
            "Metionina + Cisteína g/kg/día": None,
            "Fenilalanina + Tirosina g/kg/día": None,
            "Treonina g/kg/día": "Treonina (g)",
            "Triptófano g/kg/día": "Triptófano (g)",
            "Valina g/kg/día": "Valina (g)",
            "Proteínas g/kg/día": "Proteína (g)",
            "Fibra g/día Aia": "Fibra Dietaria (g)",
            "Carbohidratos g/día": "Carbohidratos Totales (g)",
        }
        unidades_nutriente = {
            "HIERRO* mg/día": "mg",
            "ZINC mg/día": "mg",
            "YODO mg/día": "mg",
            "CALCIO mg/día": "mg",
            "FÓSFORO mg/día": "mg",
            "MAGNESIO mg/día": "mg",
            "SODIO mg/día": "mg",
            "POTASIO mg/día": "mg",
            "Proteínas g/kg/día": "g/kg/día",
            "Fibra g/día Aia": "g",
            "Carbohidratos g/día": "g",
            "Metionina + Cisteína g/kg/día": "g/kg/día",
            "Fenilalanina + Tirosina g/kg/día": "g/kg/día",
            "Treonina g/kg/día": "g/kg/día",
            "Triptófano g/kg/día": "g/kg/día",
            "Valina g/kg/día": "g/kg/día",
            "Isoleucina g/kg/día": "g/kg/día",
            "Leucina g/kg/día": "g/kg/día",
            "Lisina g/kg/día": "g/kg/día",
            "Histidina g/kg/día": "g/kg/día",
            "Grasa Saturada": "g",
            "Grasa Monoinsaturada": "g",
            "Grasa Poliinsaturada": "g",
            "Colesterol": "mg",
        }

        rien_row = NutritionService.get_rien_row(age_days, gender)
        if rien_row is None:
            return []


        ruta_alimentos = NutritionService.CONFIG_DATA_DIR / "food_composition" / "alimentos_cartagena_completo.xlsx"
        foods_df = NutritionService._safe_read_excel(str(ruta_alimentos))

        # helper: normalizar nombre para búsqueda
        def _norm(s: Any) -> str:
            if s is None:
                return ""
            return re.sub(r'[^a-z0-9]', '', str(s).lower())

        # Use centralized tolerant column finder: NutritionService._find_food_col(foods_df, expected)

        # NOTE: removed local wrapper functions; use NutritionService._infer_col_unit and NutritionService._to_grams_per_100 directly

        # detectar y mapear columnas AMDR% en la fila RIEN: construire un mapeo token->col
        try:
            amdr_cols = [k for k in rien_row.index if isinstance(k, str) and ("%" in k or "AMDR" in str(k).upper() or "amdr" in str(k).lower())]
        except Exception:
            amdr_cols = []

        # normalizador simple: quitar acentos, paréntesis y convertir a token continuo
        def _norm_token(s: Optional[str]) -> str:
            if not s:
                return ""
            t = str(s).lower()
            t = re.sub(r'\(.*?\)', '', t)
            t = re.sub(r'[^a-z0-9]+', ' ', t)
            t = t.strip()
            return t

        amdr_map = {}
        try:
            for c in amdr_cols:
                tok = _norm_token(str(c))
                amdr_map[tok] = c
        except Exception:
            amdr_map = {}

        def _find_amdr_col_for(nutriente_name: Optional[str]) -> Optional[str]:
            """Intentar encontrar la columna AMDR que corresponda al nombre del nutriente.

            Estrategia:
             - normalizar nutriente y buscar coincidencia por token completo en amdr_map
             - luego intentar buscar por palabras clave componentes
            """

            if not nutriente_name:
                return None
            nk = _norm_token(nutriente_name)
            # búsqueda exacta tokenizada
            if nk in amdr_map:
                return amdr_map[nk]
            # intentar fragmentos
            parts = nk.split()
            for p in parts:
                for k_tok, col in amdr_map.items():
                    if p and p in k_tok:
                        return col
            return None

        table = []
        for nutriente, col_rien in nutriente_col_map.items():
            # resolver columna de alimentos de forma tolerante
            expected_col = nutriente_alimentos_map.get(nutriente)
            col_alimentos = None
            if isinstance(expected_col, (list, tuple)):
                for cand in expected_col:
                    if cand in foods_df.columns:
                        col_alimentos = cand
                        break
                    found = NutritionService._find_food_col(foods_df, cand)
                    if found:
                        col_alimentos = found
                        break
            else:
                col_alimentos = expected_col if (expected_col in foods_df.columns) else NutritionService._find_food_col(foods_df, expected_col)
            col_unit_real = NutritionService._infer_col_unit(col_alimentos) if col_alimentos else None
            unidad = unidades_nutriente.get(nutriente, "g")

            # obtener valor recomendado
            if col_rien in rien_row.index:
                raw_val = rien_row[col_rien]
            else:
                token = str(col_rien).split('.')[0].lower()
                candidates = [c for c in rien_row.index if token in str(c).lower()]
                raw_val = rien_row[candidates[0]] if candidates else None

            valor_recomendado_display, valor_recomendado_g, valor_recomendado_unit, amdr_details = NutritionService._parse_rien_value(
                raw_val, unidad, kcal_per_day=kcal_per_day, nutriente=nutriente, weight=weight
            )
            alimentos_info = []
            if "+" in (nutriente or ""):
                parts = [p.strip() for p in nutriente.split("+")]
                cols = []
                for p in parts:
                    mapped = nutriente_alimentos_map.get(p)
                    if mapped and mapped in foods_df.columns:
                        cols.append(mapped)
                    else:
                        cols.append(NutritionService._find_food_col(foods_df, mapped or p))

                alimentos_info_dicts = NutritionService._build_alimentos_for_combination(
                    foods_df, cols, valor_recomendado_g, amdr_details=amdr_details, top_n=10
                )
                for a in alimentos_info_dicts:
                    nombre = a.get("nombre")
                    suma_100g = a.get("valor_100g_sum")
                    detalle = a.get("detalle_por_100g", {})
                    display_per_100 = "/".join(str(NutritionService.format_number(detalle.get(c, 3))) for c in cols)
                    cantidad_recomendada = ""
                    try:
                        if suma_100g and suma_100g > NutritionService.MIN_VALOR_100G and valor_recomendado_g not in (None, "No dato"):
                            cantidad = (valor_recomendado_g / suma_100g) * 100.0
                            cantidad_recomendada = f"{NutritionService.format_number(cantidad,3)} g"
                    except Exception:
                        cantidad_recomendada = ""
                    alimentos_info.append([nombre, display_per_100, cantidad_recomendada])
            else:
                # BLOQUE PARA NUTRIENTES SIMPLES
                top_foods = NutritionService._build_alimentos_for_nutrient(
                    foods_df, col_alimentos, valor_recomendado_g, amdr_details=amdr_details, top_n=10
                )
                for f in top_foods:
                    valor_100_g = f.get("valor_100g")
                    display_valor_100 = NutritionService.format_number(valor_100_g, 3) if isinstance(valor_100_g, (int, float)) else ""
                    cantidad_recomendada_str = ""
                    try:
                        if valor_recomendado_g not in (None, "No dato") and valor_100_g and valor_100_g > NutritionService.MIN_VALOR_100G:
                            cantidad = (valor_recomendado_g / valor_100_g) * 100.0
                            cantidad_recomendada_str = f"{NutritionService.format_number(cantidad,3)} g"
                    except Exception:
                        cantidad_recomendada_str = ""
                    alimentos_info.append([f.get("nombre"), display_valor_100, cantidad_recomendada_str])

            table.append({
                "nutriente": nutriente,
                "valor_recomendado": valor_recomendado_display,
                "valor_recomendado_g": valor_recomendado_g,
                "valor_recomendado_unit": valor_recomendado_unit,
                "amdr_details": amdr_details,
                "alimentos": alimentos_info
            })


        # Sumar los valores recomendados de n-6 y n-3 para mostrar Grasa Poliinsaturada (g)
        try:
            n6_idx = next((i for i, item in enumerate(table) if "n-6" in item["nutriente"].lower()), None)
            n3_idx = next((i for i, item in enumerate(table) if "n-3" in item["nutriente"].lower()), None)
            n6 = table[n6_idx] if n6_idx is not None else None
            n3 = table[n3_idx] if n3_idx is not None else None
            if n6 and n3 and n6["amdr_details"] and n3["amdr_details"]:
                # Sumar rangos AMDR
                pct_lo = n6["amdr_details"]["pct_lo"] + n3["amdr_details"]["pct_lo"]
                pct_hi = n6["amdr_details"]["pct_hi"] + n3["amdr_details"]["pct_hi"]
                kcal_total = kcal_per_day
                g_lo = kcal_total * (pct_lo / 100.0) / 9.0
                g_hi = kcal_total * (pct_hi / 100.0) / 9.0
                display = f"{g_lo:.1f}-{g_hi:.1f} g ({pct_lo:.1f}-{pct_hi:.1f}% de {kcal_total:.0f} kcal)"

                # Alimentos recomendados
                col_poli = "Grasa Poliinsaturada (g)"
                top_foods_poli = NutritionService._build_alimentos_for_nutrient(
                    foods_df, col_poli, None, amdr_details=None, top_n=10
                )
                alimentos_info = []
                for f in top_foods_poli:
                    valor_100_g = f.get("valor_100g")
                    display_valor_100 = NutritionService.format_number(valor_100_g, 3) if isinstance(valor_100_g, (int, float)) else ""
                    cantidad_min = (g_lo / valor_100_g) * 100.0 if valor_100_g and valor_100_g > NutritionService.MIN_VALOR_100G else ""
                    cantidad_max = (g_hi / valor_100_g) * 100.0 if valor_100_g and valor_100_g > NutritionService.MIN_VALOR_100G else ""
                    cantidad_recomendada_str = f"{NutritionService.format_number(cantidad_min,3)}-{NutritionService.format_number(cantidad_max,3)} g" if cantidad_min and cantidad_max else ""
                    alimentos_info.append([
                        f.get("nombre"),
                        display_valor_100,
                        cantidad_recomendada_str
                    ])

                # Elimina las filas originales
                for idx in sorted([n6_idx, n3_idx], reverse=True):
                    if idx is not None:
                        table.pop(idx)
                # Agrega la fila sumada
                table.append({
                    "nutriente": "Grasa Poliinsaturada (g)",
                    "valor_recomendado": display,
                    "valor_recomendado_g": None,
                    "valor_recomendado_unit": "g",
                    "amdr_details": {
                        "pct_lo": pct_lo,
                        "pct_hi": pct_hi,
                        "g_lo": g_lo,
                        "g_hi": g_hi,
                        "kcal_per_day": kcal_total
                    },
                    "alimentos": alimentos_info
                })
        except Exception as e:
            print("Error sumando Grasa Poliinsaturada:", e)

        # --- DEPURACIÓN ---
        print("Nutrientes en tabla final (antes de filtro aminoácidos):", [item.get("nutriente") for item in table])

        return table
    
    @staticmethod
    def _safe_read_excel(path: str, **kwargs):
        """
        Lectura robusta de archivos Excel:
         - intenta pandas.read_excel con engine=openpyxl
         - si hay PermissionError copia a un temporal y lee la copia
         - si falla, intenta pd.read_excel sin engine
         - si todo falla lanza RuntimeError con contexto
        """
        # soportar cache simple: pasar cache=True/False en kwargs
        cache = kwargs.pop("cache", True)
        if cache:
            if not hasattr(NutritionService, "_excel_cache"):
                NutritionService._excel_cache = {}
            key = (str(path), tuple(sorted(kwargs.items())))
            if key in NutritionService._excel_cache:
                logger.debug("_safe_read_excel: usando cache para %s", path)
                return NutritionService._excel_cache[key]

        try:
            df = pd.read_excel(path, engine="openpyxl", **kwargs)
        except PermissionError:
            # archivo posiblemente bloqueado -> leer copia temporal
            try:
                tmp = Path(tempfile.gettempdir()) / f"tmp_read_{os.getpid()}_{Path(path).name}"
                shutil.copyfile(path, str(tmp))
                df = pd.read_excel(str(tmp), engine="openpyxl", **kwargs)
                try:
                    tmp.unlink()
                except Exception:
                    pass
            except Exception:
                df = None
        except Exception:
            df = None

        if df is None:
            try:
                df = pd.read_excel(path, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Imposible leer '{path}': {e}") from e

        if cache:
            NutritionService._excel_cache[key] = df
        return df

    @staticmethod
    def get_energy_requirement(age_days: int, weight: float, gender: str, 
                            feeding_mode: str = "breast", 
                            activity_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcula el requerimiento energético diario según edad, peso y género.
        - 0-12 meses: usa tabla de lactantes
        - 1-11 años: usa tabla de requerimientos por actividad
        - Fuera de rango: retorna "No encontrado"
        """
        # Calcular edad en meses y años
        age_months = age_days / NutritionService.DAYS_PER_MONTH
        age_years = age_days / NutritionService.DAYS_PER_YEAR

        # --- 1. Tabla de lactantes (0-12 meses) ---
        if 0 <= age_months < 12:
            try:
                ruta_lact = NutritionService.CONFIG_DATA_DIR / "food_composition" / "REQUERIMIENTO DIARIO DE ENERGÍA-LACTANTES.xlsx"
                if ruta_lact.exists():
                    df_l = pd.read_excel(str(ruta_lact))
                    # Mapeo de columnas según tipo de alimentación
                    col_indices = {
                        'breast': {'male': 3, 'female': 4},
                        'formula': {'male': 6, 'female': 7},
                        'mixed': {'male': 9, 'female': 10}
                    }
                    # Buscar la fila correcta según el rango de edad
                    def find_row_by_months(df: pd.DataFrame, months: float) -> Optional[pd.Series]:
                        col0 = df.columns[0]
                        last_valid_row = None
                        last_start = None
                        last_end = None
                        print(f"Buscando para months={months}")
                        for idx, row in df.iterrows():
                            try:
                                rango = str(row[col0]).replace(" ", "")
                                print(f"Fila {idx}: rango={rango}")
                                if "-" not in rango:
                                    continue
                                start, end = map(float, rango.split("-"))
                                last_valid_row = row
                                last_start = start
                                last_end = end
                                print(f"Comparando: {start} <= {months} < {end}")
                                if start <= months < end:
                                    print(f"Seleccionada fila {idx} para rango {rango}")
                                    return row
                            except Exception as e:
                                print(f"Fila ignorada: {e}")
                                continue
                        # Último rango
                        print(f"Chequeando último rango: {last_start} <= {months} <= {last_end}")
                        if last_valid_row is not None and last_start is not None and last_end is not None:
                            if last_start <= months <= last_end:
                                print(f"Seleccionada última fila para rango {last_start}-{last_end}")
                                return last_valid_row
                        print("No se encontró fila para la edad en meses.")
                        return None
                    row = find_row_by_months(df_l, age_months)
                    if row is not None:
                        try:
                            col_idx = col_indices[feeding_mode][gender]
                            if col_idx is not None:
                                print(f"RIEN: df_y.columns = {df_y.columns.tolist()}")
                                print(f"RIEN: Extrayendo valor de columna '{df_y.columns[col_idx]}' para género '{gender}' y actividad '{actividad}'")
                                value = row.iloc[col_idx]
                            value = float(row.iloc[col_idx])
                            return {
                                "kcal_per_kg": value,
                                "kcal_per_day": value * weight,
                                "kcal_per_kg_str": f"{value:.2f} KCAL/KG/DÍA",
                                "kcal_per_day_str": f"{value * weight:.0f} KCAL/DÍA",
                                "source": "lactantes",
                                "used_column": df_l.columns[col_idx],
                                "row_label": str(row.iloc[0]),
                                "used_table": str(ruta_lact),
                                "selected_row": row.to_dict()
                            }
                        except Exception as e:
                            logger.error(f"Error al obtener valor de columna: {e}")
                    else:
                        logger.error("No se encontró fila para la edad en meses.")
                else:
                    logger.error("No se encontró el archivo de lactantes.")
            except Exception as e:
                logger.error(f"Error leyendo tabla de lactantes: {e}")

         # --- 2. Tabla años/actividad (>=1 año) ---
        elif age_years >= 1:
            try:
                ruta_years = NutritionService.CONFIG_DATA_DIR / "food_composition" / "Requerimiento diario de energía.xlsx"
                if ruta_years.exists():
                    df_y = pd.read_excel(str(ruta_years))
                    col0 = df_y.columns[0]
                    row = None
                    last_row = None
                    last_start = last_end = None
                    # Buscar fila por rango de edad
                    for _, r in df_y.iterrows():
                        try:
                            text = str(r[col0]).replace(" ", "")
                            if "-" not in text:
                                continue
                            start, end = map(float, text.split("-"))
                            last_row = r
                            last_start, last_end = start, end
                            if start <= age_years < end:
                                row = r
                                break
                        except Exception:
                            continue
                    if row is None and last_row is not None:
                        if last_start <= age_years <= last_end:
                            row = last_row
                    if row is not None:
                        # Mapeo explícito de columnas según tu tabla
                        # (actividad, género): índice de columna
                        col_map = {
                            ("light", "male"): 2,
                            ("light", "female"): 4,
                            ("moderate", "male"): 6,
                            ("moderate", "female"): 8,
                            ("vigorous", "male"): 10,
                            ("vigorous", "female"): 12,
                        }
                        # Lógica especial para 1-6 años: siempre actividad moderada
                        if 1 <= age_years <= 6:
                            actividad = "moderate"
                        else:
                            actividad = activity_level if activity_level in ["light", "moderate", "vigorous"] else "light"
                        col_idx = col_map.get((actividad, gender))
                        if col_idx is not None:
                            value = row.iloc[col_idx]
                            if value == "-" or pd.isna(value):
                                return {
                                    "kcal_per_kg": None,
                                    "kcal_per_day": None,
                                    "kcal_per_kg_str": "No encontrado",
                                    "kcal_per_day_str": "No encontrado",
                                    "source": "years_activity",
                                    "used_column": df_y.columns[col_idx],
                                    "row_label": str(row[col0]),
                                    "used_table": str(ruta_years),
                                    "selected_row": row.to_dict()
                                }
                            value = float(value)
                            return {
                                "kcal_per_kg": value,
                                "kcal_per_day": value * weight,
                                "kcal_per_kg_str": f"{value:.2f} KCAL/KG/DÍA",
                                "kcal_per_day_str": f"{value * weight:.0f} KCAL/DÍA",
                                "source": "years_activity",
                                "used_column": df_y.columns[col_idx],
                                "row_label": str(row[col0]),
                                "used_table": str(ruta_years),
                                "selected_row": row.to_dict()
                            }
                        else:
                            logger.error("No se encontró columna adecuada para actividad y género.")
                    else:
                        logger.error("No se encontró fila para la edad en años.")
                else:
                    logger.error("No se encontró el archivo de requerimientos por años.")
            except Exception as e:
                logger.error(f"Error leyendo tabla de años/actividad: {e}")

"""""
    @staticmethod
    def generar_platos_saludables_multi(nutrient_table, requerimientos_dict, alimentos_df, num_opciones=3):
        req_proteina = requerimientos_dict.get("Proteínas g/kg/día", 0)
        req_carb = requerimientos_dict.get("Carbohidratos g/día", 0)

        def filtrar_grupo(grupo):
            return alimentos_df[alimentos_df["Grupo de Alimentos"].str.contains(grupo, case=False, na=False)]

        proteinas_df = pd.concat([
            filtrar_grupo("Pescados y mariscos"),
            filtrar_grupo("Carnes y derivados"),
            filtrar_grupo("Huevos y derivados")
        ])

        carbohidratos_df = filtrar_grupo("Cereales y derivados")

        vegetales_df = pd.concat([
            filtrar_grupo("Verduras, hortalizas y derivados"),
            filtrar_grupo("Frutas y derivados")
        ])

        leguminosas_df = filtrar_grupo("Leguminosas y derivados")

        def mejor_proteina(df):
            cols_existentes = [c for c in ["Hierro (mg)", "Zinc (mg)", "Proteína (g)"] if c in df.columns]
            return df.sort_values(cols_existentes, ascending=False).iloc[0]

        def mejor_carb(df):
            cols_existentes = [c for c in ["Carbohidratos Totales (g)", "Fibra Dietaria (g)"] if c in df.columns]
            return df.sort_values(cols_existentes, ascending=False).iloc[0]

        def mejores_vegetales(df, n=4):
            cols_existentes = [c for c in ["Vitamina C (mg)", "Calcio (mg)", "Hierro (mg)"] if c in df.columns]
            return df.sort_values(cols_existentes, ascending=False).head(n)

        def mejor_leguminosa(df):
            col = "Proteína (g)" if "Proteína (g)" in df.columns else df.columns[0]
            return df.sort_values(col, ascending=False).iloc[0]

        platos = []
        for opcion in range(num_opciones):
            plato = []
            prot = mejor_proteina(proteinas_df)
            cantidad_prot = (req_proteina * 0.9) / prot["Proteína (g)"] * 100 if prot["Proteína (g)"] > 0 else 0
            plato.append({
                "alimento": prot["Nombre Corregido"],
                "grupo": prot["Grupo de Alimentos"],
                "cantidad_g": round(cantidad_prot, 1)
            })
            leg = mejor_leguminosa(leguminosas_df)
            cantidad_leg = (req_proteina * 0.1) / leg["Proteína (g)"] * 100 if leg["Proteína (g)"] > 0 else 0
            plato.append({
                "alimento": leg["Nombre Corregido"],
                "grupo": leg["Grupo de Alimentos"],
                "cantidad_g": round(cantidad_leg, 1)
            })
            carb = mejor_carb(carbohidratos_df)
            cantidad_carb = req_carb / carb["Carbohidratos Totales (g)"] * 100 if carb["Carbohidratos Totales (g)"] > 0 else 0
            plato.append({
                "alimento": carb["Nombre Corregido"],
                "grupo": carb["Grupo de Alimentos"],
                "cantidad_g": round(cantidad_carb, 1)
            })
            vegetales = mejores_vegetales(vegetales_df, n=4)
            for _, veg in vegetales.iterrows():
                cantidad_veg = 60
                plato.append({
                    "alimento": veg["Nombre Corregido"],
                    "grupo": veg["Grupo de Alimentos"],
                    "cantidad_g": round(cantidad_veg, 1)
                })
            platos.append(plato)
        return platos

"""