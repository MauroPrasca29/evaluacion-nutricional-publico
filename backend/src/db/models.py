# -*- coding: utf-8 -*-
"""
Modelos SQLAlchemy adaptados al esquema SQL (schema.sql)
Sistema de Evaluación Nutricional Infantil
"""

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Text,
    DECIMAL, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


# ===============================
# Tabla: roles
# ===============================
class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)

    usuarios = relationship("Usuario", back_populates="rol")


# ===============================
# Tabla: usuarios
# ===============================
class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(50), unique=True, nullable=False, index=True)
    telefono = Column(String(20), unique=True, nullable=False)
    contrasena = Column(Text, nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id_rol"))
    fecha_creado = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizado = Column(DateTime(timezone=True), server_default=func.now())

    rol = relationship("Rol", back_populates="usuarios")
    seguimientos = relationship("Seguimiento", back_populates="encargado")


# ===============================
# Tabla: sedes
# ===============================
class Sede(Base):
    __tablename__ = "sedes"

    id_sede = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    municipio = Column(String(100))
    departamento = Column(String(100))
    telefono = Column(String(20))

    infantes = relationship("Infante", back_populates="sede")


# ===============================
# Tabla: acudientes
# ===============================
class Acudiente(Base):
    __tablename__ = "acudientes"

    id_acudiente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    direccion = Column(Text)
    fecha_creado = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizado = Column(DateTime(timezone=True), server_default=func.now())

    infantes = relationship("Infante", back_populates="acudiente")


# ===============================
# Tabla: infantes
# ===============================
class Infante(Base):
    __tablename__ = "infantes"

    id_infante = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(10), nullable=False)
    acudiente_id = Column(Integer, ForeignKey("acudientes.id_acudiente"))
    sede_id = Column(Integer, ForeignKey("sedes.id_sede"))
    fecha_creado = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizado = Column(DateTime(timezone=True), server_default=func.now())

    acudiente = relationship("Acudiente", back_populates="infantes")
    sede = relationship("Sede", back_populates="infantes")
    seguimientos = relationship("Seguimiento", back_populates="infante")


# ===============================
# Tabla: seguimientos
# ===============================
class Seguimiento(Base):
    __tablename__ = "seguimientos"

    id_seguimiento = Column(Integer, primary_key=True, index=True)
    infante_id = Column(Integer, ForeignKey("infantes.id_infante"))
    encargado_id = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha = Column(Date, nullable=False)
    observacion = Column(Text)

    infante = relationship("Infante", back_populates="seguimientos")
    encargado = relationship("Usuario", back_populates="seguimientos")
    datos_antropometricos = relationship("DatoAntropometrico", back_populates="seguimiento")
    examenes = relationship("Examen", back_populates="seguimiento")
    diagnosticos = relationship("Diagnostico", back_populates="seguimiento")
    reportes = relationship("ReporteIndividual", back_populates="seguimiento")
    sintomas = relationship("SeguimientoSintoma", back_populates="seguimiento")


# ===============================
# Tabla: datos_antropometricos
# ===============================
class DatoAntropometrico(Base):
    __tablename__ = "datos_antropometricos"

    id_dato = Column(Integer, primary_key=True, index=True)
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"))
    peso = Column(DECIMAL(5, 2), nullable=False)
    estatura = Column(DECIMAL(5, 2), nullable=False)
    imc = Column(DECIMAL(5, 2))
    circunferencia_braquial = Column(DECIMAL(5, 2))
    perimetro_cefalico = Column(DECIMAL(5, 2))
    pliegue_triceps = Column(DECIMAL(5, 2))
    pliegue_subescapular = Column(DECIMAL(5, 2))
    perimetro_abdominal = Column(DECIMAL(5, 2))

    seguimiento = relationship("Seguimiento", back_populates="datos_antropometricos")


# ===============================
# Tabla: examenes
# ===============================
class Examen(Base):
    __tablename__ = "examenes"

    id_examenes = Column(Integer, primary_key=True, index=True)
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"))
    hemoglobina = Column(DECIMAL(5, 2))

    seguimiento = relationship("Seguimiento", back_populates="examenes")


# ===============================
# Tabla: sintomas
# ===============================
class Sintoma(Base):
    __tablename__ = "sintomas"

    id_sintoma = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)

    seguimientos = relationship("SeguimientoSintoma", back_populates="sintoma")


# ===============================
# Tabla intermedia: seguimiento_sintomas
# ===============================
class SeguimientoSintoma(Base):
    __tablename__ = "seguimiento_sintomas"

    sintoma_id = Column(Integer, ForeignKey("sintomas.id_sintoma"), primary_key=True)
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"), primary_key=True)

    sintoma = relationship("Sintoma", back_populates="seguimientos")
    seguimiento = relationship("Seguimiento", back_populates="sintomas")


# ===============================
# Tabla: diagnosticos
# ===============================
class Diagnostico(Base):
    __tablename__ = "diagnosticos"

    id_diagnostico = Column(Integer, primary_key=True, index=True)
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"))
    diagnostico = Column(Text, nullable=False)
    recomendaciones = Column(JSON)
    fecha_generado = Column(DateTime(timezone=True), server_default=func.now())

    seguimiento = relationship("Seguimiento", back_populates="diagnosticos")


# ===============================
# Tabla: reportes_individuales
# ===============================
class ReporteIndividual(Base):
    __tablename__ = "reportes_individuales"

    id_reporte = Column(Integer, primary_key=True, index=True)
    infante_id = Column(Integer, ForeignKey("infantes.id_infante"))
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"))
    nutricionista_id = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha_reporte = Column(DateTime(timezone=True), server_default=func.now())
    archivo_url = Column(Text)
    observaciones = Column(Text)

    seguimiento = relationship("Seguimiento", back_populates="reportes")


# ===============================
# Tabla: alertas
# ===============================
class Alerta(Base):
    __tablename__ = "alertas"

    id_alerta = Column(Integer, primary_key=True, index=True)
    infante_id = Column(Integer, ForeignKey("infantes.id_infante"))
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"))
    tipo_alerta = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    estado_alerta = Column(String(20), default="pendiente")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_resuelta = Column(DateTime(timezone=True))


# ==================================
# Tabla: Evaluaciones Nutricionales
# ==================================
class EvaluacionNutricional(Base):
    """
    Almacena los resultados completos de la evaluación nutricional
    para consultas posteriores y estadísticas
    """
    __tablename__ = "evaluaciones_nutricionales"

    id_evaluacion = Column(Integer, primary_key=True, index=True)
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"), unique=True)
    
    # Datos antropométricos calculados
    imc = Column(DECIMAL(5, 2))
    
    # Z-scores
    peso_edad_zscore = Column(DECIMAL(5, 2))
    talla_edad_zscore = Column(DECIMAL(5, 2))
    imc_edad_zscore = Column(DECIMAL(5, 2))
    perimetro_cefalico_zscore = Column(DECIMAL(5, 2))
    pliegue_triceps_zscore = Column(DECIMAL(5, 2))
    pliegue_subescapular_zscore = Column(DECIMAL(5, 2))
    
    # Clasificaciones nutricionales
    clasificacion_peso_edad = Column(String(50))
    clasificacion_talla_edad = Column(String(50))
    clasificacion_peso_talla = Column(String(50))
    clasificacion_imc_edad = Column(String(50))
    clasificacion_perimetro_cefalico = Column(String(50))
    clasificacion_pliegue_triceps = Column(String(50))
    clasificacion_pliegue_subescapular = Column(String(50))
    
    # Nivel de riesgo (Bajo, Medio, Alto)
    nivel_riesgo = Column(String(20), nullable=False, index=True)
    
    # Requerimientos energéticos y nutricionales (JSON)
    requerimientos_energeticos = Column(JSON)  # {total_energy_kcal, per_kg_kcal, etc}
    requerimientos_nutrientes = Column(JSON)   # Lista de nutrientes con valores recomendados
    
    # Recomendaciones (JSON)
    recomendaciones_nutricionales = Column(JSON)  # Lista de recomendaciones
    recomendaciones_generales = Column(JSON)
    instrucciones_cuidador = Column(JSON)
    
    # Metadata
    fecha_evaluacion = Column(DateTime(timezone=True), server_default=func.now())
    
    seguimiento = relationship("Seguimiento", backref="evaluacion_nutricional")

# ===============================
# Tabla: actividad_reciente
# ===============================
class ActividadReciente(Base):
    __tablename__ = "actividad_reciente"

    id_actividad = Column(Integer, primary_key=True, index=True)
    tipo_actividad = Column(String(50), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    entidad_relacionada = Column(String(100))
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"))
    infante_id = Column(Integer, ForeignKey("infantes.id_infante"))
    seguimiento_id = Column(Integer, ForeignKey("seguimientos.id_seguimiento"))
    nivel_importancia = Column(String(20), default="normal")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    icono = Column(String(50))