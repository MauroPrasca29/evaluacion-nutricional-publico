from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from threading import Lock

router = APIRouter()

# =============================
# Pydantic Schemas
# =============================

class MeasurementCreate(BaseModel):
    date: date = Field(default_factory=date.today, description="Fecha de la toma de datos")
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
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    sex: str = Field(..., pattern=r"^(male|female|other)$")
    birth_date: date = Field(..., description="Fecha de nacimiento")
    caregiver_name: Optional[str] = Field(None, max_length=120)

class ChildCreate(ChildBase):
    measurements: List[MeasurementCreate] = Field(default_factory=list)

class ChildUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=80)
    last_name: Optional[str] = Field(None, min_length=1, max_length=80)
    sex: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    birth_date: Optional[date] = None
    caregiver_name: Optional[str] = Field(None, max_length=120)

class Child(ChildBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ChildDetail(Child):
    measurements: List[Measurement]

class PaginatedChildren(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[Child]

# =============================
# In-memory stores ("vectores")
# =============================
_children: Dict[int, ChildDetail] = {}
_measurement_seq: int = 0
_child_seq: int = 0
_lock = Lock()

# =============================
# Utils
# =============================

def _calc_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100.0
    return round(weight_kg / (h_m * h_m), 2)


def _simple_status(bmi: float) -> str:
    # Clasificación muy básica (placeholder) — migrará a motor de IA/reglas
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
# Endpoints
# =============================

@router.get("/", response_model=PaginatedChildren)
async def list_children(
    page: int = Query(1, ge=1, description="Número de página (1‑n)"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    name: Optional[str] = Query(None, description="Filtro por nombre o apellido contiene"),
    sex: Optional[str] = Query(None, pattern=r"^(male|female|other)$", description="Filtro por sexo"),
):
    """Lista de niños con paginación y filtros básicos (RF07)."""
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
    """Crea un niño con mediciones opcionales iniciales (RF01, RF05)."""
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
        # agregar mediciones iniciales si existen
        for m in payload.measurements:
            _measurement_seq += 1
            bmi = _calc_bmi(m.weight_kg, m.height_cm)
            child.measurements.append(
                Measurement(
                    id=_measurement_seq,
                    date=m.date,
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
        raise HTTPException(status_code=404, detail="Child not found")
    return child


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
            date=payload.date,
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
    """Devuelve el historial de mediciones del niño, ordenado por fecha (RF07)."""
    child = _children.get(child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return sorted(child.measurements, key=lambda m: m.date)


# =============================
# Health / metadata
# =============================
@router.get("/healthz", summary="Health check")
async def healthcheck() -> Dict[str, Any]:
    return {"status": "ok", "children_count": len(_children)}
