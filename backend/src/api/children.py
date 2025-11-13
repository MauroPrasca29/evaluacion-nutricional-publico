from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Importamos followups para reutilizar el summary clínico
from . import followups as followups_module

# OJO: aquí NO usamos /api/children, ese prefijo se agrega en main.py
router = APIRouter(tags=["children"])


# ====== Schemas ======
class ChildCreate(BaseModel):
    nombre: str = Field(..., min_length=1, examples=["Ana María Pérez Rojas"])
    fecha_nacimiento: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2021-05-10"],
    )
    genero: str = Field(..., min_length=1, examples=["F", "M"])
    sede_id: int = Field(..., ge=1, examples=[1])
    acudiente_id: Optional[int] = Field(None, ge=1)


class ChildUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    fecha_nacimiento: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    genero: Optional[str] = None
    sede_id: Optional[int] = Field(None, ge=1)
    acudiente_id: Optional[int] = Field(None, ge=1)


class ChildOut(BaseModel):
    id: int
    nombre: str
    fecha_nacimiento: str
    genero: str
    sede_id: int
    acudiente_id: Optional[int] = None


# ====== Memoria temporal (placeholder) ======
_DB: Dict[int, Dict[str, Any]] = {}
_SEQ = 0


def _next_id() -> int:
    global _SEQ
    _SEQ += 1
    return _SEQ


# ====== Helpers ======
def _sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    cols = {"nombre", "fecha_nacimiento", "genero", "sede_id", "acudiente_id"}
    return {k: v for k, v in payload.items() if k in cols}


# ====== Endpoints básicos ======
@router.get("/ping")
def ping():
    return {"ok": True, "service": "children"}


@router.get("/", response_model=List[ChildOut])
def list_children(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = list(_DB.items())
    items.sort(key=lambda kv: kv[0])
    slice_ = items[offset : offset + limit]
    return [
        ChildOut(id=cid, **data)  # type: ignore[arg-type]
        for cid, data in slice_
    ]


@router.post("/", response_model=ChildOut, status_code=201)
def create_child(payload: ChildCreate):
    data = _sanitize_payload(payload.model_dump())
    new_id = _next_id()
    _DB[new_id] = data
    return ChildOut(id=new_id, **data)  # type: ignore[arg-type]


@router.get("/{child_id}", response_model=ChildOut)
def get_child(child_id: int):
    data = _DB.get(child_id)
    if not data:
        raise HTTPException(status_code=404, detail="Child not found")
    return ChildOut(id=child_id, **data)  # type: ignore[arg-type]


@router.put("/{child_id}", response_model=ChildOut)
def update_child(child_id: int, payload: ChildUpdate):
    if child_id not in _DB:
        raise HTTPException(status_code=404, detail="Child not found")

    cur = _DB[child_id]
    updates = _sanitize_payload(payload.model_dump(exclude_unset=True))
    cur.update({k: v for k, v in updates.items() if v is not None})
    return ChildOut(id=child_id, **cur)  # type: ignore[arg-type]


@router.delete("/{child_id}", status_code=204)
def delete_child(child_id: int):
    if child_id not in _DB:
        raise HTTPException(status_code=404, detail="Child not found")
    del _DB[child_id]
    # 204 No Content → FastAPI no devuelve cuerpo
    return None


# --- Resumen combinado de niño + último seguimiento ---
@router.get("/{child_id}/summary")
def get_child_full_summary(child_id: int):
    """
    Devuelve:
    - datos básicos del niño
    - resumen clínico basado en el último followup (si existe)
    """
    data = _DB.get(child_id)
    if not data:
        raise HTTPException(status_code=404, detail="Child not found")

    child = ChildOut(id=child_id, **data)  # type: ignore[arg-type]

    # Intentamos obtener el summary de followups; si no hay, devolvemos followup_summary = None
    followup_summary = None
    try:
        followup_summary = followups_module.get_child_summary(child_id)
    except HTTPException as e:
        # Si es 404 => no tiene controles aún → lo tratamos como “sin historial”
        if e.status_code != 404:
            # Si es otro error, lo propagamos
            raise

    return {
        "child": child.model_dump(),
        "followup_summary": followup_summary,
    }
