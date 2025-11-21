from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from src.db.session import get_db
from src.db.models import Acudiente

router = APIRouter(tags=["acudientes"])

# ====== Schemas ======
class AcudienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None

class AcudienteOut(BaseModel):
    id_acudiente: int
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None

    class Config:
        from_attributes = True


# ====== Endpoints ======
class AcudienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None


@router.get("/", response_model=List[AcudienteOut])
def list_acudientes(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    db: Session = Depends(get_db)
):
    """Lista todos los acudientes con búsqueda opcional"""
    query = db.query(Acudiente)
    
    if search:
        query = query.filter(Acudiente.nombre.ilike(f"%{search}%"))
    
    acudientes = query.offset(offset).limit(limit).all()
    return acudientes


@router.post("/", response_model=AcudienteOut, status_code=status.HTTP_201_CREATED)
def create_acudiente(
    payload: AcudienteCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo acudiente"""
    new_acudiente = Acudiente(
        nombre=payload.nombre,
        telefono=payload.telefono,
        correo=payload.correo,
        direccion=payload.direccion
    )
    
    db.add(new_acudiente)
    db.commit()
    db.refresh(new_acudiente)
    
    return new_acudiente


@router.get("/{acudiente_id}", response_model=AcudienteOut)
def get_acudiente(
    acudiente_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un acudiente específico"""
    acudiente = db.query(Acudiente).filter(Acudiente.id_acudiente == acudiente_id).first()
    
    if not acudiente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Acudiente con id {acudiente_id} no encontrado"
        )
    
    return acudiente


@router.put("/{acudiente_id}", response_model=AcudienteOut)
def update_acudiente(
    acudiente_id: int,
    payload: AcudienteUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza los datos de un acudiente"""
    acudiente = db.query(Acudiente).filter(Acudiente.id_acudiente == acudiente_id).first()

    if not acudiente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Acudiente con id {acudiente_id} no encontrado"
        )

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        return acudiente

    for field, value in update_data.items():
        setattr(acudiente, field, value)

    db.commit()
    db.refresh(acudiente)

    return acudiente


@router.delete("/{acudiente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_acudiente(
    acudiente_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un acudiente existente"""
    acudiente = db.query(Acudiente).filter(Acudiente.id_acudiente == acudiente_id).first()

    if not acudiente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Acudiente con id {acudiente_id} no encontrado"
        )

    db.delete(acudiente)
    db.commit()