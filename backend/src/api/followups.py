from fastapi import FastAPI, HTTPException
from typing import List
from datetime import date
from pydantic import BaseModel

app = FastAPI()

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

# Obtener todos los follow-ups
@app.get("/followups/", response_model=List[FollowUp])
async def get_followups():
    return followups


# Crear un follow-up
@app.post("/followups/", response_model=FollowUp)
async def create_followup(followup: FollowUpCreate):
    global counter
    new_followup = FollowUp(id=counter, **followup.dict())
    followups.append(new_followup)
    counter += 1
    return new_followup


# Obtener follow-up por ID
@app.get("/followups/{followup_id}", response_model=FollowUp)
async def get_followup(followup_id: int):
    for f in followups:
        if f.id == followup_id:
            return f
    raise HTTPException(status_code=404, detail="Follow-up not found")


# Obtener follow-ups de un niño específico
@app.get("/followups/child/{child_id}", response_model=List[FollowUp])
async def get_child_followups(child_id: int):
    return [f for f in followups if f.child_id == child_id]


# Actualizar un follow-up existente
@app.put("/followups/{followup_id}", response_model=FollowUp)
async def update_followup(followup_id: int, followup: FollowUpUpdate):
    for index, f in enumerate(followups):
        if f.id == followup_id:
            updated_followup = FollowUp(id=followup_id, **followup.dict())
            followups[index] = updated_followup
            return updated_followup
    raise HTTPException(status_code=404, detail="Follow-up not found")


# Eliminar un follow-up
@app.delete("/followups/{followup_id}", response_model=dict)
async def delete_followup(followup_id: int):
    for index, f in enumerate(followups):
        if f.id == followup_id:
            followups.pop(index)
            return {"message": "Follow-up deleted successfully"}
    raise HTTPException(status_code=404, detail="Follow-up not found")
