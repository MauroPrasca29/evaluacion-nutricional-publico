from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import children as children_module  # para usar get_child_full_summary

router = APIRouter(tags=["nutrition"])


class MealRecommendation(BaseModel):
    tipo: str
    descripcion: str


class NutritionPlanOut(BaseModel):
    child_id: int
    riesgos: Dict[str, str]
    objetivos: List[str]
    recomendaciones: Dict[str, List[MealRecommendation]]


@router.get("/ping")
def ping():
    return {"ok": True, "service": "nutrition"}


def _build_objectives_and_risks(summary: Dict[str, Any]) -> tuple[Dict[str, str], List[str]]:
    """
    Recibe el summary de followups (tal cual lo devuelve followups.get_child_summary)
    y arma:
    - riesgos: {"anemia": ..., "desnutricion": ...}
    - objetivos: lista de strings
    """
    riesgos: Dict[str, str] = {}
    objetivos: List[str] = []

    clinical = summary.get("clinical_flags") or {}
    clasif_anemia: Optional[str] = clinical.get("clasificacion_anemia")
    riesgo_desnutricion: Optional[str] = clinical.get("riesgo_desnutricion")

    # Riesgo de anemia
    if clasif_anemia is None or clasif_anemia == "normal":
        riesgos["anemia"] = "bajo"
    elif clasif_anemia == "anemia_leve":
        riesgos["anemia"] = "moderado"
        objetivos.append("Mejorar el aporte de hierro a partir de alimentos accesibles y fortificados.")
    elif clasif_anemia in {"anemia_moderada", "anemia_severa"}:
        riesgos["anemia"] = "alto"
        objetivos.append("Aumentar el hierro biodisponible y coordinar valoración médica prioritaria.")

    # Riesgo de desnutrición (por ahora usamos la bandera básica del summary)
    if riesgo_desnutricion:
        riesgos["desnutricion"] = riesgo_desnutricion
    else:
        riesgos["desnutricion"] = "desconocido"

    if riesgos["desnutricion"] in {"moderado", "alto"}:
        objetivos.append("Incrementar la densidad energética de las comidas con alimentos locales.")
    elif riesgos["desnutricion"] == "bajo":
        objetivos.append("Mantener un patrón alimentario equilibrado y adecuado para la edad.")

    if not objetivos:
        objetivos.append("Mantener un buen estado nutricional con alimentación equilibrada y variada.")

    return riesgos, objetivos


def _build_local_food_plan(riesgos: Dict[str, str]) -> Dict[str, List[MealRecommendation]]:
    """
    Aquí montamos una primera versión del plan de alimentación pensando en Bolívar.
    Más adelante afinamos con una base de datos de alimentos y guías colombianas.
    """
    recs: Dict[str, List[MealRecommendation]] = {
        "desayuno": [],
        "almuerzo": [],
        "cena": [],
        "snacks": [],
    }

    anemia_risk = riesgos.get("anemia", "bajo")
    desnutricion_risk = riesgos.get("desnutricion", "bajo")

    # Ejemplos de alimentos típicos / accesibles en la región Caribe (Bolívar)
    # Aquí NO estamos usando aún una BD formal, solo una primera aproximación.
    if anemia_risk in {"moderado", "alto"}:
        recs["desayuno"].append(MealRecommendation(
            tipo="desayuno",
            descripcion="Arepa de maíz con huevo revuelto y jugo de guayaba o naranja (sin colar) para mejorar absorción de hierro."
        ))
        recs["almuerzo"].append(MealRecommendation(
            tipo="almuerzo",
            descripcion="Arroz, lentejas o fríjol cabecita negra, porción pequeña de hígado o carne, y ensalada de tomate con limón."
        ))
        recs["cena"].append(MealRecommendation(
            tipo="cena",
            descripcion="Sopa de verduras con yuca o ñame y un poco de pollo o pescado, acompañada de plátano."
        ))
        recs["snacks"].append(MealRecommendation(
            tipo="snacks",
            descripcion="Mango, guayaba, papaya o jugos naturales sin exceso de azúcar."
        ))
    else:
        recs["desayuno"].append(MealRecommendation(
            tipo="desayuno",
            descripcion="Arepa o pan con queso fresco y bebida láctea (leche, kumis) o jugo de fruta natural."
        ))
        recs["almuerzo"].append(MealRecommendation(
            tipo="almuerzo",
            descripcion="Arroz, fríjoles o lentejas, porción de pollo/pescado y ensalada sencilla con verduras disponibles."
        ))
        recs["cena"].append(MealRecommendation(
            tipo="cena",
            descripcion="Tamal o sancocho ligero con tubérculos (yuca, papa, ñame) y algo de proteína."
        ))
        recs["snacks"].append(MealRecommendation(
            tipo="snacks",
            descripcion="Frutas de temporada (mango, banano, patilla) o arepita pequeña con queso."
        ))

    # Si el riesgo de desnutrición es alto, reforzamos densidad energética
    if desnutricion_risk in {"moderado", "alto"}:
        recs["snacks"].append(MealRecommendation(
            tipo="snacks",
            descripcion="Agregar una colada espesa (avena, maíz o harina de arroz) preparada con leche o mezcla de leche y agua."
        ))

    return recs


@router.get("/child/{child_id}/plan", response_model=NutritionPlanOut)
def get_nutrition_plan_for_child(child_id: int):
    """
    Devuelve un plan alimentario básico para el niño, usando:
    - resumen combinado de niño + followups (children.get_child_full_summary)
    - flags clínicos (anemia, desnutrición)
    - alimentos típicos / accesibles de la región Caribe (versión inicial)
    """
    try:
        summary = children_module.get_child_full_summary(child_id)
    except HTTPException as e:
        if e.status_code == 404:
            raise
        raise HTTPException(status_code=500, detail="Error obteniendo resumen del niño")

    followup_summary = summary.get("followup_summary")
    if not followup_summary:
        # No tiene controles aún → plan genérico
        riesgos = {"anemia": "desconocido", "desnutricion": "desconocido"}
        objetivos = ["Realizar primer control antropométrico y de hemoglobina cuando sea posible."]
        recomendaciones = _build_local_food_plan(riesgos)
        return NutritionPlanOut(
            child_id=child_id,
            riesgos=riesgos,
            objetivos=objetivos,
            recomendaciones=recomendaciones,
        )

    riesgos, objetivos = _build_objectives_and_risks(followup_summary)
    recomendaciones = _build_local_food_plan(riesgos)

    return NutritionPlanOut(
        child_id=child_id,
        riesgos=riesgos,
        objetivos=objetivos,
        recomendaciones=recomendaciones,
    )
