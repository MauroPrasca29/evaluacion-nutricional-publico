from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Router SIN prefijo /api/followups (ese se agrega en main.py)
router = APIRouter(tags=["followups"])


# ====== Schemas ======

class FollowUpBase(BaseModel):
    child_id: int = Field(..., ge=1, examples=[1])
    fecha: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2025-11-13"],
        description="Fecha del control (YYYY-MM-DD)",
    )
    peso_kg: float = Field(..., gt=0, examples=[10.5])
    talla_cm: float = Field(..., gt=0, examples=[80.2])
    muac_cm: Optional[float] = Field(
        None,
        gt=0,
        examples=[13.5],
        description="Perímetro braquial medio (MUAC) en cm",
    )
    hb: Optional[float] = Field(
        None,
        gt=0,
        examples=[11.0],
        description="Hemoglobina en g/dL",
    )
    notas: Optional[str] = Field(None, max_length=500)
    sintomas: List[int] = Field(default_factory=list, examples=[[1, 3]])


class FollowUpCreate(FollowUpBase):
    """Payload completo para crear un seguimiento."""
    pass


class FollowUpUpdate(BaseModel):
    """Payload parcial para actualizar un seguimiento."""
    child_id: Optional[int] = Field(None, ge=1)
    fecha: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    peso_kg: Optional[float] = Field(None, gt=0)
    talla_cm: Optional[float] = Field(None, gt=0)
    muac_cm: Optional[float] = Field(None, gt=0)
    hb: Optional[float] = Field(None, gt=0)
    notas: Optional[str] = Field(None, max_length=500)
    sintomas: Optional[List[int]] = None


class FollowUpOut(FollowUpBase):
    id: int
    imc: Optional[float] = Field(
        None,
        description="IMC calculado con peso_kg y talla_cm",
    )
    clasificacion_anemia: Optional[str] = Field(
        None,
        description="normal / anemia_leve / anemia_moderada / anemia_severa",
    )


class SymptomOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None


# ====== Memoria temporal (placeholder) ======

_DB_FOLLOWUPS: Dict[int, Dict[str, Any]] = {}
_DB_SYMPTOMS: Dict[int, Dict[str, Any]] = {
    1: {"nombre": "Cansancio fácil"},
    2: {"nombre": "Palidez"},
    3: {"nombre": "Inapetencia"},
    4: {"nombre": "Mareos"},
    5: {"nombre": "Infecciones frecuentes"},
}
_SEQ = 0


def _next_id() -> int:
    global _SEQ
    _SEQ += 1
    return _SEQ


# ====== Helpers ======

def _compute_imc(peso_kg: Optional[float], talla_cm: Optional[float]) -> Optional[float]:
    if not peso_kg or not talla_cm:
        return None
    talla_m = talla_cm / 100.0
    if talla_m <= 0:
        return None
    return round(peso_kg / (talla_m ** 2), 2)


def _clasificar_anemia(hb: Optional[float]) -> Optional[str]:
    """
    Clasificación simple (hemoglobina en g/dL) para niños de 6–59 meses:
    - < 7.0  → anemia_severa
    - 7.0–9.9 → anemia_moderada
    - 10.0–10.9 → anemia_leve
    - >= 11.0 → normal
    """
    if hb is None:
        return None
    if hb < 7.0:
        return "anemia_severa"
    if hb < 10.0:
        return "anemia_moderada"
    if hb < 11.0:
        return "anemia_leve"
    return "normal"


def _sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    cols = {
        "child_id",
        "fecha",
        "peso_kg",
        "talla_cm",
        "muac_cm",
        "hb",
        "notas",
        "sintomas",
    }
    return {k: v for k, v in payload.items() if k in cols}


def _to_out_model(fid: int, data: Dict[str, Any]) -> FollowUpOut:
    imc = _compute_imc(data.get("peso_kg"), data.get("talla_cm"))
    clasif_anemia = _clasificar_anemia(data.get("hb"))
    return FollowUpOut(
        id=fid,
        imc=imc,
        clasificacion_anemia=clasif_anemia,
        **data,  # type: ignore[arg-type]
    )


# ====== Endpoints ======

@router.get("/ping")
def ping():
    return {"ok": True, "service": "followups"}


# --- Catálogo de síntomas ---

@router.get("/symptoms", response_model=List[SymptomOut])
def list_symptoms():
    return [
        SymptomOut(id=sid, **data)  # type: ignore[arg-type]
        for sid, data in sorted(_DB_SYMPTOMS.items(), key=lambda kv: kv[0])
    ]


@router.get("/symptoms/{symptom_id}", response_model=SymptomOut)
def get_symptom(symptom_id: int):
    data = _DB_SYMPTOMS.get(symptom_id)
    if not data:
        raise HTTPException(status_code=404, detail="Symptom not found")
    return SymptomOut(id=symptom_id, **data)  # type: ignore[arg-type]


@router.get("/{followup_id}/symptoms", response_model=List[SymptomOut])
def get_followup_symptoms(followup_id: int):
    data = _DB_FOLLOWUPS.get(followup_id)
    if not data:
        raise HTTPException(status_code=404, detail="FollowUp not found")
    symptom_ids: List[int] = data.get("sintomas", [])
    result: List[SymptomOut] = []
    for sid in symptom_ids:
        s = _DB_SYMPTOMS.get(sid)
        if s:
            result.append(SymptomOut(id=sid, **s))  # type: ignore[arg-type]
    return result


# --- CRUD de followups ---

@router.get("/", response_model=List[FollowUpOut])
def list_followups(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    child_id: Optional[int] = Query(
        None,
        description="Filtrar por id de niño (opcional)",
    ),
):
    items = list(_DB_FOLLOWUPS.items())
    if child_id is not None:
        items = [(fid, d) for fid, d in items if d.get("child_id") == child_id]

    items.sort(key=lambda kv: kv[0])
    slice_ = items[offset: offset + limit]
    return [
        _to_out_model(fid, data)
        for fid, data in slice_
    ]


@router.post("/", response_model=FollowUpOut, status_code=201)
def create_followup(payload: FollowUpCreate):
    data = _sanitize_payload(payload.model_dump())
    new_id = _next_id()
    _DB_FOLLOWUPS[new_id] = data
    return _to_out_model(new_id, data)


@router.get("/{followup_id}", response_model=FollowUpOut)
def get_followup(followup_id: int):
    data = _DB_FOLLOWUPS.get(followup_id)
    if not data:
        raise HTTPException(status_code=404, detail="FollowUp not found")
    return _to_out_model(followup_id, data)


@router.put("/{followup_id}", response_model=FollowUpOut)
def update_followup(followup_id: int, payload: FollowUpUpdate):
    if followup_id not in _DB_FOLLOWUPS:
        raise HTTPException(status_code=404, detail="FollowUp not found")

    cur = _DB_FOLLOWUPS[followup_id]
    updates = _sanitize_payload(payload.model_dump(exclude_unset=True))
    # Si sintomas viene explícitamente, lo respetamos tal cual
    if "sintomas" in updates and updates["sintomas"] is None:
        updates["sintomas"] = []
    cur.update({k: v for k, v in updates.items() if v is not None})
    return _to_out_model(followup_id, cur)


@router.delete("/{followup_id}", status_code=204)
def delete_followup(followup_id: int):
    if followup_id not in _DB_FOLLOWUPS:
        raise HTTPException(status_code=404, detail="FollowUp not found")
    del _DB_FOLLOWUPS[followup_id]
    # 204 No Content → FastAPI no devuelve cuerpo
    return None


# --- Último seguimiento de un niño ---

@router.get("/child/{child_id}/latest", response_model=FollowUpOut)
def get_child_latest_followup(child_id: int):
    """
    Devuelve el último seguimiento registrado para un niño dado.
    Se basa en la fecha (YYYY-MM-DD) y, en caso de empate, en el id.
    """
    candidatos = [
        (fid, data)
        for fid, data in _DB_FOLLOWUPS.items()
        if data.get("child_id") == child_id
    ]

    if not candidatos:
        raise HTTPException(
            status_code=404,
            detail="FollowUp not found for this child",
        )

    # Ordenar por fecha y luego por id, de más nuevo a más antiguo
    candidatos.sort(
        key=lambda kv: (kv[1].get("fecha") or "", kv[0]),
        reverse=True,
    )

    fid, data = candidatos[0]
    return _to_out_model(fid, data)

# --- Resumen del estado de un niño (último control) ---

@router.get("/child/{child_id}/summary")
def get_child_summary(child_id: int):
    """
    Devuelve un resumen clínico rápido del niño:
    - último control
    - conteo de controles e historial de fechas
    - banderas de riesgo (anemia, desnutrición) y síntomas
    """
    # 1) Filtrar followups del niño
    items = [
        (fid, data)
        for fid, data in _DB_FOLLOWUPS.items()
        if data.get("child_id") == child_id
    ]
    if not items:
        raise HTTPException(status_code=404, detail="No followups for this child")

    # 2) Ordenar por fecha (YYYY-MM-DD) y luego por id, y quedarnos con el más reciente
    items.sort(key=lambda kv: (kv[1].get("fecha") or "", kv[0]), reverse=True)
    latest_id, latest_data = items[0]
    latest_out = _to_out_model(latest_id, latest_data)

    # 3) Historial
    history_dates = [
        d.get("fecha")
        for _, d in items
        if d.get("fecha")
    ]
    history_count = len(items)

    # 4) Riesgo de anemia según clasificación
    anemia = latest_out.clasificacion_anemia
    if anemia in ("anemia_moderada", "anemia_severa"):
        riesgo_anemia = "alto"
    elif anemia == "anemia_leve":
        riesgo_anemia = "moderado"
    elif anemia == "normal":
        riesgo_anemia = "bajo"
    else:
        riesgo_anemia = "desconocido"

    # 5) Riesgo nutricional muy simplificado según IMC
    imc = latest_out.imc
    if imc is None:
        riesgo_desnutricion = "desconocido"
    elif imc < 14:
        riesgo_desnutricion = "alto"
    elif imc < 15.5:
        riesgo_desnutricion = "moderado"
    else:
        riesgo_desnutricion = "bajo"

    # 6) Síntomas del último control (con nombre)
    symptom_ids = latest_out.sintomas
    symptom_objs = []
    for sid in symptom_ids:
        s = _DB_SYMPTOMS.get(sid)
        if s:
            symptom_objs.append(
                {
                    "id": sid,
                    "nombre": s.get("nombre"),
                    "descripcion": s.get("descripcion"),
                }
            )

    return {
        "child_id": child_id,
        "history_count": history_count,
        "history_dates": history_dates,
        "latest_followup": latest_out.model_dump(),
        "clinical_flags": {
            "clasificacion_anemia": anemia,
            "riesgo_anemia": riesgo_anemia,
            "imc": imc,
            "riesgo_desnutricion": riesgo_desnutricion,
            "tiene_sintomas": bool(symptom_ids),
            "sintomas": symptom_objs,
        },
    }
