<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date
from pydantic import BaseModel

router = APIRouter(prefix="/followups")
=======
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(tags=["followups"])
>>>>>>> fusion-kaleth

# ====== Schemas ======
Nombre = str

class FollowupCreate(BaseModel):
    child_id: int = Field(..., ge=1)
    fecha: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2024-09-01"])
    peso_kg: Optional[float] = Field(None, ge=0)
    talla_cm: Optional[float] = Field(None, ge=0)
    observaciones: Optional[str] = None

class FollowupUpdate(BaseModel):
    fecha: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    peso_kg: Optional[float] = Field(None, ge=0)
    talla_cm: Optional[float] = Field(None, ge=0)
    observaciones: Optional[str] = None

class FollowupOut(BaseModel):
    id: int
    child_id: int
    fecha: str
    peso_kg: Optional[float] = None
    talla_cm: Optional[float] = None
    observaciones: Optional[str] = None

class SymptomCreate(BaseModel):
    codigo: str = Field(..., min_length=1, examples=["fiebre"])
    severidad: Optional[int] = Field(None, ge=1, le=5)

class SymptomOut(BaseModel):
    id_symptom: int
    followup_id: int
    codigo: str
    severidad: Optional[int] = None

# ====== Memoria temporal (placeholder) ======
_DB_F: Dict[int, Dict[str, Any]] = {}
_DB_S: Dict[int, Dict[str, Any]] = {}
_SEQ_F = 0
_SEQ_S = 0

def _next_id_f() -> int:
    global _SEQ_F
    _SEQ_F += 1
    return _SEQ_F

<<<<<<< HEAD
@router.get("/", response_model=List[FollowUp])
async def get_followups():
    """Obtener todos los follow-ups"""
    return followups
=======
def _next_id_s() -> int:
    global _SEQ_S
    _SEQ_S += 1
    return _SEQ_S
>>>>>>> fusion-kaleth

# ====== Helpers ======
def _sanitize_f(payload: Dict[str, Any]) -> Dict[str, Any]:
    cols = {"child_id", "fecha", "peso_kg", "talla_cm", "observaciones"}
    return {k: v for k, v in payload.items() if k in cols}

<<<<<<< HEAD
@router.post("/", response_model=FollowUp)
async def create_followup(followup: FollowUpCreate):
    """Crear un follow-up"""
    global counter
    new_followup = FollowUp(id=counter, **followup.dict())
    followups.append(new_followup)
    counter += 1
    return new_followup
=======
# ====== Endpoints ======
@router.get("/ping")
def ping():
    return {"ok": True, "service": "followups"}
>>>>>>> fusion-kaleth

@router.get("/", response_model=List[FollowupOut])
def list_followups(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = list(_DB_F.items())
    items.sort(key=lambda kv: kv[0])
    slice_ = items[offset : offset + limit]
    return [FollowupOut(id=fid, **data) for fid, data in slice_]  # type: ignore[arg-type]

<<<<<<< HEAD
@router.get("/{followup_id}", response_model=FollowUp)
async def get_followup(followup_id: int):
    """Obtener follow-up por ID"""
    for f in followups:
        if f.id == followup_id:
            return f
    raise HTTPException(status_code=404, detail="Follow-up not found")
=======
@router.post("/", response_model=FollowupOut, status_code=201)
def create_followup(payload: FollowupCreate):
    data = _sanitize_f(payload.model_dump())
    new_id = _next_id_f()
    _DB_F[new_id] = data
    return FollowupOut(id=new_id, **data)  # type: ignore[arg-type]
>>>>>>> fusion-kaleth

@router.get("/{followup_id}", response_model=FollowupOut)
def get_followup(followup_id: int):
    data = _DB_F.get(followup_id)
    if not data:
        raise HTTPException(status_code=404, detail="Followup not found")
    return FollowupOut(id=followup_id, **data)  # type: ignore[arg-type]

<<<<<<< HEAD
@router.get("/child/{child_id}", response_model=List[FollowUp])
async def get_child_followups(child_id: int):
    """Obtener follow-ups de un niño específico"""
    return [f for f in followups if f.child_id == child_id]
=======
@router.put("/{followup_id}", response_model=FollowupOut)
def update_followup(followup_id: int, payload: FollowupUpdate):
    if followup_id not in _DB_F:
        raise HTTPException(status_code=404, detail="Followup not found")
    cur = _DB_F[followup_id]
    updates = _sanitize_f(payload.model_dump(exclude_unset=True))
    cur.update({k: v for k, v in updates.items() if v is not None})
    return FollowupOut(id=followup_id, **cur)  # type: ignore[arg-type]
>>>>>>> fusion-kaleth

@router.delete("/{followup_id}", status_code=204)
def delete_followup(followup_id: int):
    if followup_id not in _DB_F:
        raise HTTPException(status_code=404, detail="Followup not found")
    del _DB_F[followup_id]
    # 204: sin cuerpo

<<<<<<< HEAD
@router.put("/{followup_id}", response_model=FollowUp)
async def update_followup(followup_id: int, followup: FollowUpUpdate):
    """Actualizar un follow-up existente"""
    for index, f in enumerate(followups):
        if f.id == followup_id:
            updated_followup = FollowUp(id=followup_id, **followup.dict())
            followups[index] = updated_followup
            return updated_followup
    raise HTTPException(status_code=404, detail="Follow-up not found")


@router.delete("/{followup_id}", response_model=dict)
async def delete_followup(followup_id: int):
    """Eliminar un follow-up"""
    for index, f in enumerate(followups):
        if f.id == followup_id:
            followups.pop(index)
            return {"message": "Follow-up deleted successfully"}
    raise HTTPException(status_code=404, detail="Follow-up not found")
=======
@router.post("/{followup_id}/symptoms", response_model=SymptomOut, status_code=201)
def add_symptom(followup_id: int, payload: SymptomCreate):
    if followup_id not in _DB_F:
        raise HTTPException(status_code=404, detail="Followup not found")
    new_sid = _next_id_s()
    _DB_S[new_sid] = {
        "followup_id": followup_id,
        "codigo": payload.codigo,
        "severidad": payload.severidad,
    }
    return SymptomOut(id_symptom=new_sid, **_DB_S[new_sid])  # type: ignore[arg-type]

@router.get("/symptoms/{symptom_id}", response_model=SymptomOut)
def get_symptom(symptom_id: int):
    data = _DB_S.get(symptom_id)
    if not data:
        raise HTTPException(status_code=404, detail="Symptom not found")
    return SymptomOut(id_symptom=symptom_id, **data)  # type: ignore[arg-type]
>>>>>>> fusion-kaleth
