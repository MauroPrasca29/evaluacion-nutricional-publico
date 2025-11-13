from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

from . import children as children_module  # para usar get_child_full_summary

router = APIRouter(tags=["nutrition"])


# --- Modelos simples (solo para typing) ---

def _build_plan_from_summary(
    child_id: int,
    summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Construye el plan alimentario a partir del resumen clínico de followups.
    summary corresponde a lo que devuelve children.get_child_full_summary(child_id).
    """
    followup_summary = summary.get("followup_summary") or {}
    clinical_flags = followup_summary.get("clinical_flags") or {}

    riesgo_anemia = clinical_flags.get("riesgo_anemia", "desconocido")
    riesgo_desnutricion = clinical_flags.get("riesgo_desnutricion", "desconocido")

    # Objetivos generales (muy básicos de momento)
    objetivos: List[str] = [
        "Mantener un patrón alimentario equilibrado y adecuado para la edad.",
    ]

    if riesgo_anemia in ("moderado", "alto"):
        objetivos.insert(
            0,
            "Mejorar el aporte de hierro a partir de alimentos accesibles y fortificados.",
        )

    if riesgo_desnutricion in ("moderado", "alto"):
        objetivos.append(
            "Asegurar un aporte calórico adecuado con alimentos locales de buena densidad energética."
        )

    # Recomendaciones básicas usando alimentos típicos de Bolívar
    recomendaciones: Dict[str, List[Dict[str, str]]] = {
        "desayuno": [
            {
                "tipo": "desayuno",
                "descripcion": (
                    "Arepa de maíz con huevo revuelto y jugo de guayaba o naranja "
                    "(sin colar) para mejorar absorción de hierro."
                ),
            }
        ],
        "almuerzo": [
            {
                "tipo": "almuerzo",
                "descripcion": (
                    "Arroz, lentejas o fríjol cabecita negra, porción pequeña de hígado "
                    "o carne, y ensalada de tomate con limón."
                ),
            }
        ],
        "cena": [
            {
                "tipo": "cena",
                "descripcion": (
                    "Sopa de verduras con yuca o ñame y un poco de pollo o pescado, "
                    "acompañada de plátano."
                ),
            }
        ],
        "snacks": [
            {
                "tipo": "snacks",
                "descripcion": (
                    "Mango, guayaba, papaya o jugos naturales sin exceso de azúcar."
                ),
            }
        ],
    }

    return {
        "child_id": child_id,
        "riesgos": {
            "anemia": riesgo_anemia,
            "desnutricion": riesgo_desnutricion,
        },
        "objetivos": objetivos,
        "recomendaciones": recomendaciones,
    }


# --- Función reutilizable desde otros módulos (reports.py) ---

def get_child_plan(child_id: int) -> Dict[str, Any]:
    """
    Función que puede ser usada tanto por el endpoint HTTP como por otros módulos
    (por ejemplo, reports.py) para obtener el plan alimentario de un niño.
    """
    # Obtener el resumen combinado de niño + clínica
    child_summary = children_module.get_child_full_summary(child_id)

    # Si no hay resumen de followups, lanzamos 404
    followup_summary = child_summary.get("followup_summary")
    if not followup_summary:
        raise HTTPException(
            status_code=404,
            detail="No hay datos clínicos suficientes para generar un plan nutricional.",
        )

    return _build_plan_from_summary(child_id, child_summary)


# --- Endpoints HTTP ---


@router.get("/ping")
def ping():
    return {"ok": True, "service": "nutrition"}


@router.get("/child/{child_id}/plan")
def get_child_plan_endpoint(child_id: int) -> Dict[str, Any]:
    """
    Endpoint HTTP para obtener un plan alimentario básico
    para un niño específico.
    """
    return get_child_plan(child_id)
