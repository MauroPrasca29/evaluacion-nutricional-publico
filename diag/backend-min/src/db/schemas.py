# -*- coding: utf-8 -*-
"""
Pydantic Schemas
==========================
Definición de modelos Pydantic para validación y serialización de datos
basados en los modelos SQLAlchemy del sistema de evaluación nutricional.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List


# ===============================
# Esquemas: Rol
# ===============================
class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolCreate(RolBase):
    pass


class Rol(RolBase):
    id_rol: int

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Usuario
# ===============================
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str


class UsuarioCreate(UsuarioBase):
    contrasena: str


class UsuarioResponse(UsuarioBase):
    id_usuario: int
    fecha_creado: datetime

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Sede
# ===============================
class SedeBase(BaseModel):
    nombre: str
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    telefono: Optional[str] = None


class SedeCreate(SedeBase):
    pass


class Sede(SedeBase):
    id_sede: int

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Acudiente
# ===============================
class AcudienteBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None


class AcudienteCreate(AcudienteBase):
    pass


class Acudiente(AcudienteBase):
    id_acudiente: int
    fecha_creado: datetime

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Infante
# ===============================
class InfanteBase(BaseModel):
    nombre: str
    fecha_nacimiento: date
    genero: str
    acudiente_id: Optional[int] = None
    sede_id: Optional[int] = None


class InfanteCreate(InfanteBase):
    pass


class Infante(InfanteBase):
    id_infante: int
    fecha_creado: datetime

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Seguimiento
# ===============================
class SeguimientoBase(BaseModel):
    infante_id: int
    encargado_id: Optional[int] = None
    fecha: date
    observacion: Optional[str] = None


class SeguimientoCreate(SeguimientoBase):
    pass


class Seguimiento(SeguimientoBase):
    id_seguimiento: int

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Dato Antropométrico
# ===============================
class DatoAntropometricoBase(BaseModel):
    seguimiento_id: int
    peso: float
    estatura: float
    imc: Optional[float] = None
    circunferencia_braquial: Optional[float] = None
    perimetro_cefalico: Optional[float] = None
    pliegue_cutaneo: Optional[float] = None
    perimetro_abdominal: Optional[float] = None


class DatoAntropometricoCreate(DatoAntropometricoBase):
    pass


class DatoAntropometrico(DatoAntropometricoBase):
    id_dato: int

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Examen
# ===============================
class ExamenBase(BaseModel):
    seguimiento_id: int
    hemoglobina: Optional[float] = None


class ExamenCreate(ExamenBase):
    pass


class Examen(ExamenBase):
    id_examenes: int

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Síntoma
# ===============================
class SintomaBase(BaseModel):
    nombre: str


class SintomaCreate(SintomaBase):
    pass


class Sintoma(SintomaBase):
    id_sintoma: int

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Diagnóstico
# ===============================
class DiagnosticoBase(BaseModel):
    seguimiento_id: int
    diagnostico: str
    recomendaciones: Optional[dict] = None


class DiagnosticoCreate(DiagnosticoBase):
    pass


class Diagnostico(DiagnosticoBase):
    id_diagnostico: int
    fecha_generado: datetime

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Reporte Individual
# ===============================
class ReporteIndividualBase(BaseModel):
    infante_id: int
    seguimiento_id: int
    nutricionista_id: Optional[int] = None
    archivo_url: Optional[str] = None
    observaciones: Optional[str] = None


class ReporteIndividualCreate(ReporteIndividualBase):
    pass


class ReporteIndividual(ReporteIndividualBase):
    id_reporte: int
    fecha_reporte: datetime

    class Config:
        orm_mode = True


# ===============================
# Esquemas: Alerta
# ===============================
class AlertaBase(BaseModel):
    infante_id: int
    seguimiento_id: Optional[int] = None
    tipo_alerta: str
    mensaje: str
    estado_alerta: Optional[str] = "pendiente"


class AlertaCreate(AlertaBase):
    pass


class Alerta(AlertaBase):
    id_alerta: int
    fecha_creacion: datetime
    fecha_resuelta: Optional[datetime] = None

    class Config:
        orm_mode = True
