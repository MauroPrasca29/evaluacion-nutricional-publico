# backend/src/api/children.py

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.db.session import get_db
from src.db.models import Infante
from src.db.schemas import InfanteCreate, Infante as InfanteSchema

router = APIRouter(tags=["children"])

# ====== Schemas de Request/Response ======
class ChildCreate(BaseModel):
    nombre: str = Field(..., min_length=1, examples=["Ana María Pérez Rojas"])
    fecha_nacimiento: date = Field(..., examples=["2021-05-10"])
    genero: str = Field(..., pattern=r"^[MF]$", examples=["F", "M"])
    sede_id: Optional[int] = Field(None, ge=1, examples=[1])
    acudiente_id: Optional[int] = Field(None, ge=1)

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Ana María Pérez Rojas",
                "fecha_nacimiento": "2021-05-10",
                "genero": "F",
                "sede_id": 1,
                "acudiente_id": 1
            }
        }


class ChildUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = Field(None, pattern=r"^[MF]$")
    sede_id: Optional[int] = Field(None, ge=1)
    acudiente_id: Optional[int] = None


class ChildOut(BaseModel):
    id_infante: int
    nombre: str
    fecha_nacimiento: date
    genero: str
    sede_id: Optional[int] = None
    acudiente_id: Optional[int] = None

    class Config:
        from_attributes = True


# ====== Endpoints ======
@router.get("/ping")
def ping():
    """Endpoint de health check para el servicio de children"""
    return {"ok": True, "service": "children"}


@router.get("/", response_model=List[ChildOut])
def list_children(
    limit: int = Query(50, ge=1, le=500, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los infantes con paginación
    """
    children = db.query(Infante).offset(offset).limit(limit).all()
    return children


@router.post("/", response_model=ChildOut, status_code=status.HTTP_201_CREATED)
def create_child(
    payload: ChildCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo registro de infante
    """
    # Verificar que la sede existe si se proporciona
    if payload.sede_id:
        from src.db.models import Sede
        sede = db.query(Sede).filter(Sede.id_sede == payload.sede_id).first()
        if not sede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con id {payload.sede_id} no encontrada"
            )
    
    # Verificar que el acudiente existe si se proporciona
    if payload.acudiente_id:
        from src.db.models import Acudiente
        acudiente = db.query(Acudiente).filter(Acudiente.id_acudiente == payload.acudiente_id).first()
        if not acudiente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Acudiente con id {payload.acudiente_id} no encontrado"
            )
    
    # Crear el nuevo infante
    new_child = Infante(
        nombre=payload.nombre,
        fecha_nacimiento=payload.fecha_nacimiento,
        genero=payload.genero,
        sede_id=payload.sede_id,
        acudiente_id=payload.acudiente_id
    )
    
    db.add(new_child)
    db.commit()
    db.refresh(new_child)
    
    return new_child


@router.get("/{child_id}", response_model=ChildOut)
def get_child(
    child_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un infante específico por ID
    """
    child = db.query(Infante).filter(Infante.id_infante == child_id).first()
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infante con id {child_id} no encontrado"
        )
    
    return child


@router.put("/{child_id}", response_model=ChildOut)
def update_child(
    child_id: int,
    payload: ChildUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un infante existente
    """
    child = db.query(Infante).filter(Infante.id_infante == child_id).first()
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infante con id {child_id} no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = payload.model_dump(exclude_unset=True)
    
    # Verificar relaciones si se actualizan
    if "sede_id" in update_data and update_data["sede_id"]:
        from src.db.models import Sede
        sede = db.query(Sede).filter(Sede.id_sede == update_data["sede_id"]).first()
        if not sede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sede con id {update_data['sede_id']} no encontrada"
            )
    
    if "acudiente_id" in update_data and update_data["acudiente_id"]:
        from src.db.models import Acudiente
        acudiente = db.query(Acudiente).filter(Acudiente.id_acudiente == update_data["acudiente_id"]).first()
        if not acudiente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Acudiente con id {update_data['acudiente_id']} no encontrado"
            )
    
    # Aplicar actualizaciones
    for key, value in update_data.items():
        setattr(child, key, value)
    
    db.commit()
    db.refresh(child)
    
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un infante
    """
    child = db.query(Infante).filter(Infante.id_infante == child_id).first()
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infante con id {child_id} no encontrado"
        )
    
    db.delete(child)
    db.commit()
    
    return None


@router.get("/{child_id}/followups")
def get_child_followups(
    child_id: int,
    db: Session = Depends(get_db)
):

    """
    Obtiene todos los seguimientos de un infante específico con datos antropométricos
    """
    child = db.query(Infante).filter(Infante.id_infante == child_id).first()
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infante con id {child_id} no encontrado"
        )
    
    # Obtener seguimientos con datos antropométricos
    from src.db.models import Seguimiento, DatoAntropometrico
    from sqlalchemy.orm import joinedload
    
    # CAMBIO: Ordenar por ID descendente en lugar de fecha
    seguimientos = db.query(Seguimiento).filter(
        Seguimiento.infante_id == child_id
    ).order_by(Seguimiento.id_seguimiento.desc()).all()
    
    result = []
    for seg in seguimientos:
        # Obtener datos antropométricos del seguimiento
        datos_antropo = db.query(DatoAntropometrico).filter(
            DatoAntropometrico.seguimiento_id == seg.id_seguimiento
        ).first()
        
        seguimiento_data = {
            "id_seguimiento": seg.id_seguimiento,
            "fecha": seg.fecha.isoformat() if seg.fecha else None,
            "observacion": seg.observacion,
            "encargado_id": seg.encargado_id,
            "peso": float(datos_antropo.peso) if datos_antropo and datos_antropo.peso else None,
            "estatura": float(datos_antropo.estatura) if datos_antropo and datos_antropo.estatura else None,
            "imc": float(datos_antropo.imc) if datos_antropo and datos_antropo.imc else None,
            "circunferencia_braquial": float(datos_antropo.circunferencia_braquial) if datos_antropo and datos_antropo.circunferencia_braquial else None,
            "perimetro_cefalico": float(datos_antropo.perimetro_cefalico) if datos_antropo and datos_antropo.perimetro_cefalico else None,
            "pliegue_triceps": float(datos_antropo.pliegue_triceps) if datos_antropo and datos_antropo.pliegue_triceps else None,
            "pliegue_subescapular": float(datos_antropo.pliegue_subescapular) if datos_antropo and datos_antropo.pliegue_subescapular else None,
            "perimetro_abdominal": float(datos_antropo.perimetro_abdominal) if datos_antropo and datos_antropo.perimetro_abdominal else None,
        }
        result.append(seguimiento_data)
    
    return result


# Mantener el endpoint antiguo por compatibilidad
@router.get("/{child_id}/seguimientos", response_model=List[dict])
def get_child_seguimientos(
    child_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los seguimientos de un infante específico (endpoint de compatibilidad)
    Redirige a /followups
    """
    return get_child_followups(child_id, db)