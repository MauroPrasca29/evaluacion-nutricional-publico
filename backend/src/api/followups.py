from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal

from src.db.session import get_db
from src.db.models import Seguimiento, Infante, DatoAntropometrico, Examen

router = APIRouter(tags=["followups"])

# ====== Schemas ======

class FollowupCreate(BaseModel):
    infante_id: int = Field(..., ge=1)
    fecha: date
    observacion: Optional[str] = None
    # Observaciones clínicas (síntomas y signos físicos concatenados)
    observaciones_clinicas: Optional[List[str]] = None
    # Datos antropométricos
    peso: float = Field(..., ge=0)
    estatura: float = Field(..., ge=0)
    imc: Optional[float] = None
    circunferencia_braquial: Optional[float] = Field(None, ge=0)
    perimetro_cefalico: Optional[float] = Field(None, ge=0)
    pliegue_cutaneo: Optional[float] = Field(None, ge=0)
    perimetro_abdominal: Optional[float] = Field(None, ge=0)
    # Exámenes
    hemoglobina: Optional[float] = Field(None, ge=0)
    # Foto
    foto_ojo_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "infante_id": 1,
                "fecha": "2024-11-15",
                "observacion": "Observaciones del nutricionista sobre la evaluación",
                "observaciones_clinicas": [
                    "Síntomas: Pérdida de apetito, Fatiga o debilidad",
                    "Signos físicos: Palidez en piel o mucosas"
                ],
                "peso": 15.5,
                "estatura": 95.0,
                "imc": 17.2,
                "circunferencia_braquial": 16.5,
                "perimetro_cefalico": 48.0,
                "pliegue_cutaneo": 12.5,
                "perimetro_abdominal": 52.0,
                "hemoglobina": 11.5,
                "foto_ojo_url": "https://example.com/photos/eye123.jpg"
            }
        }


class FollowupOut(BaseModel):
    id_seguimiento: int
    infante_id: int
    fecha: date
    observacion: Optional[str] = None
    # Datos antropométricos
    peso: Optional[float] = None
    estatura: Optional[float] = None
    imc: Optional[float] = None
    circunferencia_braquial: Optional[float] = None
    perimetro_cefalico: Optional[float] = None
    pliegue_cutaneo: Optional[float] = None
    perimetro_abdominal: Optional[float] = None
    # Exámenes
    hemoglobina: Optional[float] = None
    # Foto
    foto_ojo_url: Optional[str] = None

    class Config:
        from_attributes = True


class FollowupDetailOut(BaseModel):
    seguimiento: FollowupOut
    infante_nombre: str

    class Config:
        from_attributes = True


# ====== Endpoints ======

@router.get("/ping")
def ping():
    return {"ok": True, "service": "followups"}


@router.get("/", response_model=List[FollowupOut])
def list_followups(
    infante_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Lista todos los seguimientos, opcionalmente filtrados por infante_id
    """
    query = db.query(Seguimiento)
    
    if infante_id:
        query = query.filter(Seguimiento.infante_id == infante_id)
    
    seguimientos = query.order_by(Seguimiento.fecha.desc()).offset(offset).limit(limit).all()
    
    # Construir respuesta con datos antropométricos y exámenes
    result = []
    for seg in seguimientos:
        # Obtener datos antropométricos
        dato_antro = db.query(DatoAntropometrico).filter(
            DatoAntropometrico.seguimiento_id == seg.id_seguimiento
        ).first()
        
        # Obtener exámenes
        examen = db.query(Examen).filter(
            Examen.seguimiento_id == seg.id_seguimiento
        ).first()
        
        result.append(FollowupOut(
            id_seguimiento=seg.id_seguimiento,
            infante_id=seg.infante_id,
            fecha=seg.fecha,
            observacion=seg.observacion,
            peso=float(dato_antro.peso) if dato_antro and dato_antro.peso else None,
            estatura=float(dato_antro.estatura) if dato_antro and dato_antro.estatura else None,
            imc=float(dato_antro.imc) if dato_antro and dato_antro.imc else None,
            circunferencia_braquial=float(dato_antro.circunferencia_braquial) if dato_antro and dato_antro.circunferencia_braquial else None,
            perimetro_cefalico=float(dato_antro.perimetro_cefalico) if dato_antro and dato_antro.perimetro_cefalico else None,
            pliegue_cutaneo=float(dato_antro.pliegue_cutaneo) if dato_antro and dato_antro.pliegue_cutaneo else None,
            perimetro_abdominal=float(dato_antro.perimetro_abdominal) if dato_antro and dato_antro.perimetro_abdominal else None,
            hemoglobina=float(examen.hemoglobina) if examen and examen.hemoglobina else None,
            foto_ojo_url=None  # Agregar cuando implementes almacenamiento de fotos
        ))
    
    return result


@router.post("/", response_model=FollowupOut, status_code=status.HTTP_201_CREATED)
def create_followup(payload: FollowupCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo seguimiento con datos antropométricos y exámenes
    """
    # Verificar que el infante existe
    infante = db.query(Infante).filter(Infante.id_infante == payload.infante_id).first()
    if not infante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infante con id {payload.infante_id} no encontrado"
        )
    
    # Concatenar observaciones clínicas con observaciones del nutricionista
    observacion_completa = ""
    if payload.observaciones_clinicas:
        observacion_completa = "\n".join(payload.observaciones_clinicas)
        if payload.observacion:
            observacion_completa += f"\n\nObservaciones del nutricionista:\n{payload.observacion}"
    else:
        observacion_completa = payload.observacion or ""
    
    # Crear seguimiento
    nuevo_seguimiento = Seguimiento(
        infante_id=payload.infante_id,
        fecha=payload.fecha,
        observacion=observacion_completa,
        encargado_id=None  # TODO: Obtener del usuario autenticado
    )
    db.add(nuevo_seguimiento)
    db.flush()  # Para obtener el id_seguimiento
    
    # Calcular IMC si no viene
    imc = payload.imc
    if not imc and payload.peso and payload.estatura:
        altura_metros = payload.estatura / 100
        imc = payload.peso / (altura_metros * altura_metros)
    
    # Crear datos antropométricos
    datos_antro = DatoAntropometrico(
        seguimiento_id=nuevo_seguimiento.id_seguimiento,
        peso=Decimal(str(payload.peso)),
        estatura=Decimal(str(payload.estatura)),
        imc=Decimal(str(round(imc, 2))) if imc else None,
        circunferencia_braquial=Decimal(str(payload.circunferencia_braquial)) if payload.circunferencia_braquial else None,
        perimetro_cefalico=Decimal(str(payload.perimetro_cefalico)) if payload.perimetro_cefalico else None,
        pliegue_cutaneo=Decimal(str(payload.pliegue_cutaneo)) if payload.pliegue_cutaneo else None,
        perimetro_abdominal=Decimal(str(payload.perimetro_abdominal)) if payload.perimetro_abdominal else None
    )
    db.add(datos_antro)
    
    # Crear exámenes si hay hemoglobina
    if payload.hemoglobina:
        examen = Examen(
            seguimiento_id=nuevo_seguimiento.id_seguimiento,
            hemoglobina=Decimal(str(payload.hemoglobina))
        )
        db.add(examen)
    
    db.commit()
    db.refresh(nuevo_seguimiento)
    
    return FollowupOut(
        id_seguimiento=nuevo_seguimiento.id_seguimiento,
        infante_id=nuevo_seguimiento.infante_id,
        fecha=nuevo_seguimiento.fecha,
        observacion=nuevo_seguimiento.observacion,
        peso=float(datos_antro.peso),
        estatura=float(datos_antro.estatura),
        imc=float(datos_antro.imc) if datos_antro.imc else None,
        circunferencia_braquial=float(datos_antro.circunferencia_braquial) if datos_antro.circunferencia_braquial else None,
        perimetro_cefalico=float(datos_antro.perimetro_cefalico) if datos_antro.perimetro_cefalico else None,
        pliegue_cutaneo=float(datos_antro.pliegue_cutaneo) if datos_antro.pliegue_cutaneo else None,
        perimetro_abdominal=float(datos_antro.perimetro_abdominal) if datos_antro.perimetro_abdominal else None,
        hemoglobina=float(payload.hemoglobina) if payload.hemoglobina else None,
        foto_ojo_url=payload.foto_ojo_url
    )


@router.get("/{followup_id}", response_model=FollowupOut)
def get_followup(followup_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un seguimiento específico por ID
    """
    seguimiento = db.query(Seguimiento).filter(
        Seguimiento.id_seguimiento == followup_id
    ).first()
    
    if not seguimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seguimiento con id {followup_id} no encontrado"
        )
    
    # Obtener datos antropométricos
    dato_antro = db.query(DatoAntropometrico).filter(
        DatoAntropometrico.seguimiento_id == followup_id
    ).first()
    
    # Obtener exámenes
    examen = db.query(Examen).filter(
        Examen.seguimiento_id == followup_id
    ).first()
    
    return FollowupOut(
        id_seguimiento=seguimiento.id_seguimiento,
        infante_id=seguimiento.infante_id,
        fecha=seguimiento.fecha,
        observacion=seguimiento.observacion,
        peso=float(dato_antro.peso) if dato_antro and dato_antro.peso else None,
        estatura=float(dato_antro.estatura) if dato_antro and dato_antro.estatura else None,
        imc=float(dato_antro.imc) if dato_antro and dato_antro.imc else None,
        circunferencia_braquial=float(dato_antro.circunferencia_braquial) if dato_antro and dato_antro.circunferencia_braquial else None,
        perimetro_cefalico=float(dato_antro.perimetro_cefalico) if dato_antro and dato_antro.perimetro_cefalico else None,
        pliegue_cutaneo=float(dato_antro.pliegue_cutaneo) if dato_antro and dato_antro.pliegue_cutaneo else None,
        perimetro_abdominal=float(dato_antro.perimetro_abdominal) if dato_antro and dato_antro.perimetro_abdominal else None,
        hemoglobina=float(examen.hemoglobina) if examen and examen.hemoglobina else None,
        foto_ojo_url=None
    )


@router.delete("/{followup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_followup(followup_id: int, db: Session = Depends(get_db)):
    """
    Elimina un seguimiento (CASCADE eliminará datos antropométricos y exámenes)
    """
    seguimiento = db.query(Seguimiento).filter(
        Seguimiento.id_seguimiento == followup_id
    ).first()
    
    if not seguimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seguimiento con id {followup_id} no encontrado"
        )
    
    db.delete(seguimiento)
    db.commit()