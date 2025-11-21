from sqlalchemy.orm import Session
from src.db.models import ActividadReciente

class ActivityService:
    
    @staticmethod
    def registrar_nuevo_nino(db: Session, nombre_nino: str, usuario_id: int, infante_id: int):
        """Registra la actividad de un nuevo niño"""
        actividad = ActividadReciente(
            tipo_actividad="nuevo_nino",
            descripcion=f"Nuevo niño registrado",
            entidad_relacionada=nombre_nino,
            usuario_id=usuario_id,
            infante_id=infante_id,
            nivel_importancia="normal",
            icono="user-plus"
        )
        db.add(actividad)
        db.commit()
    
    @staticmethod
    def registrar_seguimiento(db: Session, nombre_nino: str, usuario_id: int, infante_id: int, seguimiento_id: int):
        """Registra la actividad de un nuevo seguimiento"""
        actividad = ActividadReciente(
            tipo_actividad="seguimiento",
            descripcion=f"Seguimiento completado para",
            entidad_relacionada=nombre_nino,
            usuario_id=usuario_id,
            infante_id=infante_id,
            seguimiento_id=seguimiento_id,
            nivel_importancia="normal",
            icono="file-text"
        )
        db.add(actividad)
        db.commit()
    
    @staticmethod
    def registrar_alerta(db: Session, nombre_nino: str, nivel_riesgo: str, infante_id: int, seguimiento_id: int):
        """Registra una alerta de riesgo nutricional"""
        nivel_importancia = "alta" if nivel_riesgo == "Alto" else "media"
        
        actividad = ActividadReciente(
            tipo_actividad="alerta",
            descripcion=f"Nueva alerta de {'sobrepeso' if 'sobre' in nivel_riesgo.lower() else 'desnutrición'} para",
            entidad_relacionada=nombre_nino,
            infante_id=infante_id,
            seguimiento_id=seguimiento_id,
            nivel_importancia=nivel_importancia,
            icono="alert-triangle"
        )
        db.add(actividad)
        db.commit()
    
    @staticmethod
    def registrar_importacion(db: Session, sede_nombre: str, cantidad: int, usuario_id: int):
        """Registra una importación de datos"""
        actividad = ActividadReciente(
            tipo_actividad="importacion",
            descripcion=f"Importación de datos completada",
            entidad_relacionada=sede_nombre,
            usuario_id=usuario_id,
            nivel_importancia="normal",
            icono="upload"
        )
        db.add(actividad)
        db.commit()
    
    @staticmethod
    def obtener_recientes(db: Session, limit: int = 4):
        """Obtiene las actividades más recientes"""
        return db.query(ActividadReciente)\
            .order_by(ActividadReciente.fecha_creacion.desc())\
            .limit(limit)\
            .all()