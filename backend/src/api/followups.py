from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date
from pydantic import BaseModel

router = APIRouter(prefix="/followups")

# ---- Modelos ----
class FollowUpBase(BaseModel):
    child_id: int
    date: date
    notes: str | None = None

class FollowUpCreate(FollowUpBase):
    pass

class FollowUpUpdate(FollowUpBase):
    pass

class FollowUp(FollowUpBase):
    id: int


# ---- Datos en memoria ----
followups: List[FollowUp] = []
counter = 1


# ---- Endpoints ----

@router.get("/", response_model=List[FollowUp])
async def get_followups():
    """Obtener todos los follow-ups"""
    return followups


@router.post("/", response_model=FollowUp)
async def create_followup(followup: FollowUpCreate):
    """Crear un follow-up"""
    global counter
    new_followup = FollowUp(id=counter, **followup.dict())
    followups.append(new_followup)
    counter += 1
    return new_followup


@router.get("/{followup_id}", response_model=FollowUp)
async def get_followup(followup_id: int):
    """Obtener follow-up por ID"""
    for f in followups:
        if f.id == followup_id:
            return f
    raise HTTPException(status_code=404, detail="Follow-up not found")


@router.get("/child/{child_id}", response_model=List[FollowUp])
async def get_child_followups(child_id: int):
    """Obtener follow-ups de un niño específico"""
    return [f for f in followups if f.child_id == child_id]


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
