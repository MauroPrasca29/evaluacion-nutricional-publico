# backend/src/api/children.py

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.db.session import get_db
from src.db.models import Infante, Seguimiento
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


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas para el dashboard:
    - Total de niños registrados
    - Alertas activas (niños con riesgo alto en su última evaluación)
    """
    from src.db.models import EvaluacionNutricional
    from sqlalchemy import func
    
    # Total de niños
    total_children = db.query(Infante).count()
    
    # Alertas activas: niños con riesgo alto en su última evaluación
    # Subconsulta para obtener el seguimiento más reciente de cada infante
    subq = (
        db.query(
            Seguimiento.infante_id,
            func.max(Seguimiento.id_seguimiento).label('ultimo_seguimiento')
        )
        .group_by(Seguimiento.infante_id)
        .subquery()
    )
    
    # Contar evaluaciones con riesgo alto en los últimos seguimientos
    active_alerts = (
        db.query(func.count(EvaluacionNutricional.id_evaluacion))
        .join(subq, EvaluacionNutricional.seguimiento_id == subq.c.ultimo_seguimiento)
        .filter(EvaluacionNutricional.nivel_riesgo == 'Alto')
        .scalar()
    ) or 0
    
    return {
        "total_children": total_children,
        "active_alerts": active_alerts
    }

@router.get("/nutritional-stats")
def get_nutritional_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas nutricionales detalladas:
    - Por rangos de edad (0-2, 3-5, 6-8, 9-11 años)
    - Distribución general por nivel de riesgo
    - Distribución por género
    - Estadísticas por sede
    """
    from src.db.models import EvaluacionNutricional, Sede
    from sqlalchemy import func, case, extract
    from datetime import datetime, date
    
    # Función para calcular edad en años desde fecha de nacimiento
    def calcular_edad_años(fecha_nac):
        if not fecha_nac:
            return None
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad
    
    # Obtener todos los infantes con su última evaluación
    subq_ultimo_seguimiento = (
        db.query(
            Seguimiento.infante_id,
            func.max(Seguimiento.id_seguimiento).label('ultimo_seguimiento')
        )
        .group_by(Seguimiento.infante_id)
        .subquery()
    )
    
    # Query principal: infantes con su última evaluación
    infantes_evaluaciones = (
        db.query(
            Infante.id_infante,
            Infante.fecha_nacimiento,
            Infante.genero,
            Infante.sede_id,
            EvaluacionNutricional.nivel_riesgo
        )
        .join(subq_ultimo_seguimiento, Infante.id_infante == subq_ultimo_seguimiento.c.infante_id)
        .outerjoin(
            EvaluacionNutricional,
            EvaluacionNutricional.seguimiento_id == subq_ultimo_seguimiento.c.ultimo_seguimiento
        )
        .all()
    )
    
    # Procesar datos por rangos de edad
    edad_ranges = {
        "0-2 años": {"normal": 0, "bajo": 0, "medio": 0, "alto": 0},
        "3-5 años": {"normal": 0, "bajo": 0, "medio": 0, "alto": 0},
        "6-8 años": {"normal": 0, "bajo": 0, "medio": 0, "alto": 0},
        "9-11 años": {"normal": 0, "bajo": 0, "medio": 0, "alto": 0},
    }
    
    # Distribución general
    distribucion_general = {"normal": 0, "bajo": 0, "medio": 0, "alto": 0}
    
    # Distribución por género
    distribucion_genero = {
        "M": {"normal": 0, "bajo": 0, "medio": 0, "alto": 0},
        "F": {"normal": 0, "bajo": 0, "medio": 0, "alto": 0}
    }
    
    # Procesar cada infante
    for infante in infantes_evaluaciones:
        edad = calcular_edad_años(infante.fecha_nacimiento)
        if edad is None:
            continue
        
        # Normalizar nivel de riesgo (manejar None como "normal")
        nivel = (infante.nivel_riesgo or "Normal").lower()
        if nivel == "normal" or nivel == "bajo":
            riesgo_key = "normal"
        elif nivel == "medio":
            riesgo_key = "bajo"
        elif nivel == "alto":
            riesgo_key = "medio"
        else:
            riesgo_key = "alto"
        
        # Mapeo más simple basado en el nivel real
        if nivel in ["normal", "bajo"]:
            riesgo_key = "normal"
        elif nivel == "medio":
            riesgo_key = "bajo"
        elif nivel == "alto":
            riesgo_key = "medio"
        else:
            riesgo_key = "alto"
        
        # Clasificar por edad
        if 0 <= edad <= 2:
            edad_ranges["0-2 años"][riesgo_key] += 1
        elif 3 <= edad <= 5:
            edad_ranges["3-5 años"][riesgo_key] += 1
        elif 6 <= edad <= 8:
            edad_ranges["6-8 años"][riesgo_key] += 1
        elif 9 <= edad <= 11:
            edad_ranges["9-11 años"][riesgo_key] += 1
        
        # Distribución general
        distribucion_general[riesgo_key] += 1
        
        # Distribución por género
        if infante.genero in ["M", "F"]:
            distribucion_genero[infante.genero][riesgo_key] += 1
    
    # Obtener estadísticas por sede
    sedes = db.query(Sede).all()
    sedes_stats = []
    
    for sede in sedes:
        infantes_sede = [i for i in infantes_evaluaciones if i.sede_id == sede.id_sede]
        total = len(infantes_sede)
        
        if total > 0:
            normal = sum(1 for i in infantes_sede if (i.nivel_riesgo or "Normal").lower() in ["normal", "bajo"])
            alertas = total - normal
            
            sedes_stats.append({
                "sede": sede.nombre,
                "total": total,
                "normal": normal,
                "alertas": alertas
            })
    
    return {
        "por_edad": [
            {"ageGroup": k, **v} for k, v in edad_ranges.items()
        ],
        "general": distribucion_general,
        "por_genero": [
            {"genero": "Masculino", **distribucion_genero["M"]},
            {"genero": "Femenino", **distribucion_genero["F"]}
        ],
        "por_sede": sedes_stats
    }


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
    
    # Registrar actividad
    from src.services.activity_service import ActivityService
    ActivityService.registrar_nuevo_nino(
        db=db,
        nombre_nino=new_child.nombre,
        usuario_id=1,  # TODO: Obtener del token JWT
        infante_id=new_child.id_infante
    )
    
    return new_child

@router.get("/recent-activity")
def get_recent_activity(db: Session = Depends(get_db), limit: int = 4):
    """
    Obtiene las actividades más recientes del sistema con información del usuario
    """
    from src.db.models import ActividadReciente, Usuario
    from datetime import datetime
    
    actividades = db.query(ActividadReciente, Usuario)\
        .outerjoin(Usuario, ActividadReciente.usuario_id == Usuario.id_usuario)\
        .order_by(ActividadReciente.fecha_creacion.desc())\
        .limit(limit)\
        .all()
    
    resultado = []
    for act, usuario in actividades:
        # Calcular tiempo relativo
        ahora = datetime.now(act.fecha_creacion.tzinfo)
        diferencia = ahora - act.fecha_creacion
        
        if diferencia.days > 0:
            tiempo = f"Hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
        elif diferencia.seconds >= 3600:
            horas = diferencia.seconds // 3600
            tiempo = f"Hace {horas} hora{'s' if horas > 1 else ''}"
        else:
            minutos = max(1, diferencia.seconds // 60)  # Mínimo 1 minuto
            tiempo = f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        
        # Construir texto con el nombre del usuario si está disponible
        usuario_nombre = usuario.nombre if usuario else "Usuario"
        
        resultado.append({
            "id": act.id_actividad,
            "text": act.descripcion,
            "subject": act.entidad_relacionada,
            "time": tiempo,
            "icon": act.icono,
            "tipo": act.tipo_actividad,
            "nivel": act.nivel_importancia,
            "usuario": usuario_nombre
        })
    
    return resultado

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


@router.get("/alerts")
def get_active_alerts(db: Session = Depends(get_db), limit: int = 10):
    """
    Obtiene notificaciones recientes (alertas, seguimientos, importaciones)
    """
    from src.db.models import ActividadReciente, Infante, Usuario
    from datetime import datetime
    
    # Obtener actividades recientes con joins
    actividades = db.query(ActividadReciente, Infante, Usuario)\
        .outerjoin(Infante, ActividadReciente.infante_id == Infante.id_infante)\
        .outerjoin(Usuario, ActividadReciente.usuario_id == Usuario.id_usuario)\
        .order_by(ActividadReciente.fecha_creacion.desc())\
        .limit(limit)\
        .all()
    
    resultado = []
    for actividad, infante, usuario in actividades:
        # Calcular tiempo relativo
        ahora = datetime.now(actividad.fecha_creacion.tzinfo) if actividad.fecha_creacion.tzinfo else datetime.now()
        diferencia = ahora - actividad.fecha_creacion
        
        if diferencia.days > 0:
            tiempo = f"Hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
        elif diferencia.seconds >= 3600:
            horas = diferencia.seconds // 3600
            tiempo = f"Hace {horas} hora{'s' if horas > 1 else ''}"
        else:
            minutos = max(1, diferencia.seconds // 60)
            tiempo = f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        
        # Determinar tipo y mensaje según el tipo de actividad
        if actividad.tipo_actividad == "alerta":
            tipo = "alert" if actividad.nivel_importancia == "alta" else "warning"
            titulo = "Alerta Nutricional" if actividad.nivel_importancia == "alta" else "Advertencia Nutricional"
            mensaje = f"{actividad.descripcion} {actividad.entidad_relacionada}"
            mostrar_infante = actividad.entidad_relacionada
            mostrar_usuario = None
        elif actividad.tipo_actividad == "seguimiento":
            tipo = "info"
            titulo = "Seguimiento Completado"
            mensaje = f"{actividad.descripcion} {actividad.entidad_relacionada}"
            mostrar_infante = actividad.entidad_relacionada
            mostrar_usuario = usuario.nombre if usuario else "Usuario"
        elif actividad.tipo_actividad == "importacion":
            tipo = "success"
            titulo = "Importación de Datos"
            mensaje = f"{actividad.descripcion}"
            mostrar_infante = actividad.entidad_relacionada  # Nombre de la sede
            mostrar_usuario = usuario.nombre if usuario else "Usuario"
        else:
            tipo = "info"
            titulo = actividad.descripcion
            mensaje = actividad.entidad_relacionada or ""
            mostrar_infante = actividad.entidad_relacionada
            mostrar_usuario = usuario.nombre if usuario else None
        
        resultado.append({
            "id": actividad.id_actividad,
            "type": tipo,
            "title": titulo,
            "message": mensaje,
            "time": tiempo,
            "read": False,
            "childName": mostrar_infante,
            "infanteId": actividad.infante_id,
            "seguimientoId": actividad.seguimiento_id,
            "userName": mostrar_usuario,
            "tipoActividad": actividad.tipo_actividad
        })
    
    return resultado

@router.get("/alerts/count")
def get_alerts_count(db: Session = Depends(get_db)):
    """
    Obtiene el conteo de alertas sin leer (últimas 24 horas)
    """
    from src.db.models import ActividadReciente
    from datetime import datetime, timedelta
    
    hace_24h = datetime.now() - timedelta(hours=24)
    
    count = db.query(ActividadReciente)\
        .filter(ActividadReciente.tipo_actividad == "alerta")\
        .filter(ActividadReciente.fecha_creacion >= hace_24h)\
        .count()
    
    return {"count": count}