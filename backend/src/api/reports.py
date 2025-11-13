from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from . import children as children_module
from . import nutrition as nutrition_module

# Este router se monta en main.py con prefix="/api/reports"
# Aquí usamos prefix="/reports" para que las rutas finales queden:
#   /api/reports/reports/...
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/")
def list_available_reports() -> Dict[str, Any]:
    """
    Devuelve un listado de endpoints de reporte disponibles.
    Útil para que el frontend descubra qué puede consultar.
    """
    return {
        "endpoints": [
            "GET /api/reports/reports/",
            "GET /api/reports/reports/import/{import_id}/summary",
            "GET /api/reports/reports/import/{import_id}/export",
            "GET /api/reports/reports/child/{child_id}/full",
        ]
    }


# --- Placeholders de los reportes por importación (para no romper el Front) ---

@router.get("/import/{import_id}/summary")
def get_import_summary(import_id: int) -> Dict[str, Any]:
    """
    Placeholder de reporte-resumen por importación.
    En la rama de diagnóstico no usamos DB real, así que devolvemos
    un esquema simple que el frontend pueda consumir sin romperse.
    """
    if import_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid import_id")

    return {
        "import_id": import_id,
        "status": "not_implemented_in_debug_mode",
        "message": (
            "El resumen por importación no está implementado en esta rama "
            "de diagnóstico sin base de datos."
        ),
    }


@router.get("/import/{import_id}/export")
def export_import_report(import_id: int) -> Dict[str, Any]:
    """
    Placeholder de exportación de reporte por importación.
    En la rama de diagnóstico solo devolvemos un objeto JSON simbólico.
    """
    if import_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid import_id")

    return {
        "import_id": import_id,
        "status": "not_implemented_in_debug_mode",
        "message": (
            "La exportación de reportes por importación no está implementada "
            "en esta rama de diagnóstico sin base de datos."
        ),
    }


# ---------- Helpers ----------

def _deep_convert(obj: Any) -> Any:
    """
    Convierte recursivamente modelos Pydantic (v1 o v2) a dict,
    listas y dicts anidados también. Cualquier otra cosa la deja igual.
    """
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    # Pydantic v1
    if hasattr(obj, "dict"):
        return obj.dict()
    # dict anidado
    if isinstance(obj, dict):
        return {k: _deep_convert(v) for k, v in obj.items()}
    # lista/tupla anidada
    if isinstance(obj, (list, tuple)):
        return [_deep_convert(v) for v in obj]
    return obj


# --- Reporte completo por niño (datos, clínica, nutrición) ---

@router.get("/child/{child_id}/full")
def get_child_full_report(child_id: int) -> Dict[str, Any]:
    """
    Reporte integral de un niño:
    - Datos básicos (children)
    - Resumen clínico (followups, vía children)
    - Plan nutricional básico (nutrition)
    """

    # 1) Resumen combinado de datos + clínica
    try:
        child_summary_raw = children_module.get_child_full_summary(child_id)
    except HTTPException as e:
        # Propagamos el 404 si el niño no existe
        if e.status_code == 404:
            raise
        # Otros errores inesperados se devuelven como 500
        raise HTTPException(status_code=500, detail="Error fetching child summary")

    # Aseguramos que TODO sea JSON-safe
    child_summary = _deep_convert(child_summary_raw)

    # 2) Plan nutricional
    try:
        nutrition_plan_raw = nutrition_module.get_child_plan(child_id)
    except HTTPException as e:
        # Si falla porque no hay followups o algo similar, devolvemos un aviso
        if e.status_code == 404:
            nutrition_plan = {
                "child_id": child_id,
                "riesgos": {},
                "objetivos": [],
                "recomendaciones": {},
                "warning": "No se pudo generar plan nutricional (posible falta de datos clínicos).",
            }
        else:
            raise HTTPException(status_code=500, detail="Error generating nutrition plan")
    else:
        nutrition_plan = _deep_convert(nutrition_plan_raw)

    # 3) Extra: sacamos algunos flags clínicos directos
    followup_summary = None
    clinical_flags = None

    if isinstance(child_summary, dict):
        followup_summary = child_summary.get("followup_summary")
        if isinstance(followup_summary, dict):
            clinical_flags = followup_summary.get("clinical_flags")

    return {
        "child": child_summary.get("child") if isinstance(child_summary, dict) else None,
        "clinical_summary": followup_summary,
        "clinical_flags": clinical_flags,
        "nutrition_plan": nutrition_plan,
    }
