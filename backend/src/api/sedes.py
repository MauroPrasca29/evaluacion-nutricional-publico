from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.db.session import get_db
from src.db.models import Sede

router = APIRouter(tags=["sedes"])

# ====== Schemas de Request/Response ======
class SedeOut(BaseModel):
    id_sede: int
    nombre: str
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    telefono: Optional[str] = None

    class Config:
        from_attributes = True


# ====== Endpoints ======
@router.get("/", response_model=List[SedeOut])
def list_sedes(
    limit: int = Query(50, ge=1, le=500, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    db: Session = Depends(get_db)
):
    """
    Lista todas las sedes con paginación
    """
    sedes = db.query(Sede).offset(offset).limit(limit).all()
    return sedes


@router.get("/{sede_id}", response_model=SedeOut)
def get_sede(
    sede_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una sede específica por ID
    """
    sede = db.query(Sede).filter(Sede.id_sede == sede_id).first()
    
    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede con id {sede_id} no encontrada"
        )
    
    return sede