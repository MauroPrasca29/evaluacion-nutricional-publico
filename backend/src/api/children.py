<<<<<<< HEAD
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator, constr
=======
>>>>>>> fusion-kaleth
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

<<<<<<< HEAD
# Router (sin prefix, se gestiona en main.py)
router = APIRouter(tags=["Children"])

# =============================
# Pydantic Schemas
# =============================

class MeasurementCreate(BaseModel):
    measurement_date: date = Field(default_factory=date.today, description="Fecha de la toma de datos")
    weight_kg: float = Field(..., gt=0, lt=200, description="Peso en kilogramos")
    height_cm: float = Field(..., gt=20, lt=220, description="Talla en centímetros")
    diet_notes: Optional[str] = Field(None, max_length=500, description="Notas dietarias breves")

    @field_validator("height_cm")
    @classmethod
    def check_height(cls, v: float) -> float:
        if v < 20 or v > 220:
            raise ValueError("Altura fuera de rango razonable (20–220 cm)")
        return v

class Measurement(MeasurementCreate):
    id: int
    bmi: float
    nutritional_status: str

class ChildBase(BaseModel):
    first_name: constr(min_length=1, max_length=80)
    last_name: constr(min_length=1, max_length=80)
    sex: str = Field(..., pattern=r"^(male|female|other)$")
    birth_date: date = Field(..., description="Fecha de nacimiento")
    caregiver_name: Optional[str] = Field(None, max_length=120)

class ChildCreate(ChildBase):
    measurements: List[MeasurementCreate] = Field(default_factory=list)

class ChildUpdate(BaseModel):
    first_name: Optional[constr(min_length=1, max_length=80)] = None
    last_name: Optional[constr(min_length=1, max_length=80)] = None
    sex: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    birth_date: Optional[date] = None
    caregiver_name: Optional[str] = Field(None, max_length=120)
=======
router = APIRouter(tags=["children"])

# ====== Schemas ======
class ChildCreate(BaseModel):
    nombre: str = Field(..., min_length=1, examples=["Ana María Pérez Rojas"])
    fecha_nacimiento: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2021-05-10"])
    genero: str = Field(..., min_length=1, examples=["F", "M"])
    sede_id: int = Field(..., ge=1, examples=[1])
    acudiente_id: Optional[int] = Field(None, ge=1)

class ChildUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    fecha_nacimiento: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    genero: Optional[str] = None
    sede_id: Optional[int] = Field(None, ge=1)
    acudiente_id: Optional[int] = Field(None, ge=1)
>>>>>>> fusion-kaleth

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

<<<<<<< HEAD
# =============================
# In-memory stores
# =============================
_children: Dict[int, ChildDetail] = {}
_measurement_seq: int = 0
_child_seq: int = 0
_lock = Lock()
=======
# ====== Helpers ======
def _sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    cols = {"nombre", "fecha_nacimiento", "genero", "sede_id", "acudiente_id"}
    return {k: v for k, v in payload.items() if k in cols}
>>>>>>> fusion-kaleth

# ====== Endpoints ======
@router.get("/ping")
def ping():
    return {"ok": True, "service": "children"}

<<<<<<< HEAD
def _calc_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100.0
    return round(weight_kg / (h_m * h_m), 2)

def _simple_status(bmi: float) -> str:
    if bmi < 14:
        return "underweight"
    if bmi < 18.5:
        return "risk_underweight"
    if bmi <= 24.9:
        return "normal"
    if bmi <= 29.9:
        return "overweight"
    return "obese"

# =============================
# Endpoints (CRUD + extras)
# =============================

@router.get("/", response_model=PaginatedChildren)
async def list_children(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    sex: Optional[str] = Query(None, pattern=r"^(male|female|other)$"),
):
    """Lista de niños con paginación y filtros (RF07)."""
    items = list(_children.values())
    if name:
        needle = name.strip().lower()
        items = [c for c in items if needle in c.first_name.lower() or needle in c.last_name.lower()]
    if sex:
        items = [c for c in items if c.sex == sex]

    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = [Child(**c.model_dump(exclude={"measurements"})) for c in items[start:end]]

    return PaginatedChildren(total=total, page=page, per_page=per_page, items=page_items)

@router.post("/", response_model=ChildDetail, status_code=status.HTTP_201_CREATED)
async def create_child(payload: ChildCreate):
    """Crea un niño con mediciones iniciales opcionales (RF01, RF05)."""
    global _child_seq, _measurement_seq
    with _lock:
        _child_seq += 1
        child_id = _child_seq
        now = datetime.utcnow()
        child = ChildDetail(
            id=child_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            sex=payload.sex,
            birth_date=payload.birth_date,
            caregiver_name=payload.caregiver_name,
            created_at=now,
            updated_at=now,
            measurements=[],
        )
        for m in payload.measurements:
            _measurement_seq += 1
            bmi = _calc_bmi(m.weight_kg, m.height_cm)
            child.measurements.append(
                Measurement(
                    id=_measurement_seq,
                    measurement_date=m.measurement_date,
                    weight_kg=m.weight_kg,
                    height_cm=m.height_cm,
                    diet_notes=m.diet_notes,
                    bmi=bmi,
                    nutritional_status=_simple_status(bmi),
                )
            )
        _children[child_id] = child
        return child

@router.get("/{child_id}", response_model=ChildDetail)
async def get_child(child_id: int):
    child = _children.get(child_id)
    if not child:
=======
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
>>>>>>> fusion-kaleth
        raise HTTPException(status_code=404, detail="Child not found")
    return ChildOut(id=child_id, **data)  # type: ignore[arg-type]

<<<<<<< HEAD
@router.put("/{child_id}", response_model=ChildDetail)
async def update_child(child_id: int, payload: ChildUpdate):
    with _lock:
        child = _children.get(child_id)
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(child, k, v)
        child.updated_at = datetime.utcnow()
        _children[child_id] = child
        return child

@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(child_id: int):
    with _lock:
        if child_id not in _children:
            raise HTTPException(status_code=404, detail="Child not found")
        _children.pop(child_id)
    return None

@router.post("/{child_id}/measurements", response_model=Measurement, status_code=status.HTTP_201_CREATED)
async def add_measurement(child_id: int, payload: MeasurementCreate):
    """Agrega una medición al historial del niño (RF05)."""
    global _measurement_seq
    with _lock:
        child = _children.get(child_id)
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        _measurement_seq += 1
        bmi = _calc_bmi(payload.weight_kg, payload.height_cm)
        m = Measurement(
            id=_measurement_seq,
            measurement_date=payload.measurement_date,
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            diet_notes=payload.diet_notes,
            bmi=bmi,
            nutritional_status=_simple_status(bmi),
        )
        child.measurements.append(m)
        child.updated_at = datetime.utcnow()
        return m

@router.get("/{child_id}/history", response_model=List[Measurement])
async def get_history(child_id: int):
    """Devuelve el historial de mediciones del niño (RF07)."""
    child = _children.get(child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return sorted(child.measurements, key=lambda m: m.measurement_date)

# =============================
# Health
# =============================
@router.get("/healthz", summary="Health check")
async def healthcheck() -> Dict[str, Any]:
    return {"status": "ok", "children_count": len(_children)}
=======
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
    # 204 No Content -> FastAPI no devolverá cuerpo
>>>>>>> fusion-kaleth
