# -*- coding: utf-8 -*-
"""
Auth API
--------
Registro de usuarios, login con JWT y perfil (/me).

- Usa modelo SQLAlchemy: db.models.Usuario
- Usa Pydantic: db.schemas.UsuarioCreate, UsuarioResponse
- DB session: db.session.get_db
- JWT: jose (python-jose)
- Hash: passlib (bcrypt) con normalización a 72 bytes
"""

from datetime import datetime, timedelta
import os
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.db.session import get_db
from src.db.models import Usuario
from src.db.schemas import UsuarioCreate, UsuarioResponse

# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------
# Estos valores vienen del .env; se usan defaults seguros si no están.
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# IMPORTANT: el tokenUrl debe coincidir con el prefijo que pone main.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["auth"])  # el prefijo /api/auth lo añade main.py


# ------------------------------------------------------------
# Utilidades de password y JWT
# ------------------------------------------------------------
def _bcrypt_normalize(password: str) -> str:
    """
    Bcrypt solo usa los primeros 72 bytes.
    Normalizamos a utf-8, truncamos a 72 bytes y devolvemos str.
    """
    if not isinstance(password, str):
        raise ValueError("La contraseña debe ser texto.")
    pw_bytes = password.strip().encode("utf-8")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
    return pw_bytes.decode("utf-8", "ignore")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(_bcrypt_normalize(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_bcrypt_normalize(plain_password), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------------------------------------
# Esquemas auxiliares para Auth
# ------------------------------------------------------------
class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class MeResponse(BaseModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
    telefono: str
    rol_id: Optional[int] = None
    rol_nombre: Optional[str] = None
    es_admin: bool = False


# ------------------------------------------------------------
# Registro
# ------------------------------------------------------------
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Registra un nuevo usuario.
    Solo disponible para administradores.
    """
    # Verificar que quien crea el usuario sea admin
    current_user = _get_current_user(db, token)
    _require_admin(current_user)
    
    # Validar duplicados
    if db.query(Usuario).filter(Usuario.correo == usuario.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    if db.query(Usuario).filter(Usuario.telefono == usuario.telefono).first():
        raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

    # Crear usuario con contraseña hasheada
    nuevo = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        telefono=usuario.telefono,
        contrasena=get_password_hash(usuario.contrasena),
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # Respuesta segura (sin devolver hash)
    return UsuarioResponse(
        id_usuario=nuevo.id_usuario,
        nombre=nuevo.nombre,
        correo=nuevo.correo,
        telefono=nuevo.telefono,
        fecha_creado=nuevo.fecha_creado,
    )


# ------------------------------------------------------------
# Login (JSON) - más cómodo para Postman
# ------------------------------------------------------------
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Login con JSON:
    {
      "correo": "admin@example.com",
      "contrasena": "12345678"
    }
    """
    user = db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    if not user or not verify_password(payload.contrasena, user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": user.correo, "uid": user.id_usuario})
    return TokenResponse(access_token=token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)


# ------------------------------------------------------------
# Token (OAuth2PasswordRequestForm) - útil para frontends/SDKs
# ------------------------------------------------------------
@router.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login estilo OAuth2 con form-data:
      username = correo
      password = contrasena
    """
    user = db.query(Usuario).filter(Usuario.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": user.correo, "uid": user.id_usuario})
    return TokenResponse(access_token=token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)


# ------------------------------------------------------------
# Perfil actual (/me) protegido por Bearer Token
# ------------------------------------------------------------
def _get_current_user(db: Session, token: str) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")  # email del usuario
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not user:
        raise credentials_exception
    return user


def _require_admin(user: Usuario) -> None:
    """
    Verifica que el usuario tenga rol de administrador.
    Lanza HTTPException 403 si no es admin.
    """
    if not user.rol or user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores pueden realizar esta acción."
        )


@router.get("/me", response_model=MeResponse)
def me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = _get_current_user(db, token)
    return MeResponse(
        id_usuario=user.id_usuario,
        nombre=user.nombre,
        correo=user.correo,
        telefono=user.telefono,
        rol_id=user.rol_id,
        rol_nombre=user.rol.nombre if user.rol else None,
        es_admin=user.rol.nombre == "Administrador" if user.rol else False,
    )


# ------------------------------------------------------------
# Actualizar perfil del usuario
# ------------------------------------------------------------
class UpdateProfileRequest(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None


@router.put("/me", response_model=MeResponse)
def update_profile(
    profile_data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Actualiza el perfil del usuario autenticado.
    Solo se actualizan los campos proporcionados.
    """
    user = _get_current_user(db, token)
    
    # Actualizar solo los campos proporcionados
    if profile_data.nombre is not None:
        user.nombre = profile_data.nombre
    
    if profile_data.telefono is not None:
        # Validar que el teléfono no esté en uso por otro usuario
        existing = db.query(Usuario).filter(
            Usuario.telefono == profile_data.telefono,
            Usuario.id_usuario != user.id_usuario
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El teléfono ya está en uso")
        user.telefono = profile_data.telefono
    
    user.fecha_actualizado = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return MeResponse(
        id_usuario=user.id_usuario,
        nombre=user.nombre,
        correo=user.correo,
        telefono=user.telefono,
    )


# ------------------------------------------------------------
# Cambiar contraseña
# ------------------------------------------------------------
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Cambia la contraseña del usuario autenticado.
    Requiere la contraseña actual para validación.
    """
    user = _get_current_user(db, token)
    
    # Verificar contraseña actual
    if not verify_password(password_data.current_password, user.contrasena):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Actualizar contraseña
    user.contrasena = get_password_hash(password_data.new_password)
    user.fecha_actualizado = datetime.utcnow()
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}


# ------------------------------------------------------------
# Listar todos los usuarios (solo admin)
# ------------------------------------------------------------
class UsuarioListResponse(BaseModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
    telefono: str
    rol_id: Optional[int] = None
    fecha_creado: datetime
    fecha_actualizado: datetime

    class Config:
        orm_mode = True


@router.get("/users", response_model=List[UsuarioListResponse])
def list_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todos los usuarios del sistema.
    Solo disponible para administradores.
    """
    current_user = _get_current_user(db, token)
    
    # Verificar que el usuario actual sea admin
    _require_admin(current_user)
    
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios


# ------------------------------------------------------------
# Restablecer contraseña de un usuario (admin)
# ------------------------------------------------------------
class ResetPasswordRequest(BaseModel):
    new_password: str


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    password_data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Restablece la contraseña de un usuario específico.
    Solo disponible para administradores.
    """
    # Validar que el usuario actual esté autenticado
    current_user = _get_current_user(db, token)
    
    # Verificar que el usuario actual sea admin
    _require_admin(current_user)
    
    # Buscar el usuario a modificar
    target_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # No permitir que un usuario se restablezca a sí mismo usando este endpoint
    if target_user.id_usuario == current_user.id_usuario:
        raise HTTPException(
            status_code=400,
            detail="Use el endpoint /change-password para cambiar su propia contraseña"
        )
    
    # Actualizar contraseña
    target_user.contrasena = get_password_hash(password_data.new_password)
    target_user.fecha_actualizado = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Contraseña restablecida exitosamente para {target_user.nombre}",
        "usuario_id": target_user.id_usuario,
        "usuario_nombre": target_user.nombre
    }


# ------------------------------------------------------------
# Listar todos los roles disponibles
# ------------------------------------------------------------
class RolResponse(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        orm_mode = True


@router.get("/roles", response_model=List[RolResponse])
def list_roles(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Lista todos los roles disponibles en el sistema.
    Disponible para usuarios autenticados.
    """
    _get_current_user(db, token)  # Solo validar que esté autenticado
    
    from src.db.models import Rol
    roles = db.query(Rol).all()
    return roles


# ------------------------------------------------------------
# Actualizar usuario (admin)
# ------------------------------------------------------------
class UpdateUserRequest(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    rol_id: Optional[int] = None


@router.put("/users/{user_id}", response_model=UsuarioListResponse)
def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Actualiza los datos de un usuario específico.
    Solo disponible para administradores.
    """
    # Validar que el usuario actual esté autenticado
    current_user = _get_current_user(db, token)
    
    print(f"🔍 DEBUG update_user:")
    print(f"  - current_user (quien hace la petición): {current_user.nombre} (id={current_user.id_usuario}, email={current_user.correo})")
    print(f"  - user_id (usuario a modificar): {user_id}")
    print(f"  - user_data: {user_data}")
    
    # Verificar que el usuario actual sea admin
    _require_admin(current_user)
    
    # Buscar el usuario a modificar
    target_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    print(f"  - target_user ANTES: {target_user.nombre} (id={target_user.id_usuario}, email={target_user.correo}, rol_id={target_user.rol_id})")
    
    # Actualizar campos proporcionados
    if user_data.nombre is not None:
        target_user.nombre = user_data.nombre
    
    if user_data.telefono is not None:
        # Validar que el teléfono no esté en uso por otro usuario
        existing = db.query(Usuario).filter(
            Usuario.telefono == user_data.telefono,
            Usuario.id_usuario != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El teléfono ya está en uso")
        target_user.telefono = user_data.telefono
    
    if user_data.rol_id is not None:
        # Validar que el rol exista
        from src.db.models import Rol
        rol = db.query(Rol).filter(Rol.id_rol == user_data.rol_id).first()
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        target_user.rol_id = user_data.rol_id
    
    target_user.fecha_actualizado = datetime.utcnow()
    db.commit()
    db.refresh(target_user)
    
    print(f"  - target_user DESPUÉS: {target_user.nombre} (id={target_user.id_usuario}, email={target_user.correo}, rol_id={target_user.rol_id})")
    
    return target_user


# ------------------------------------------------------------
# Eliminar usuario (admin)
# ------------------------------------------------------------
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Elimina un usuario del sistema.
    Solo disponible para administradores.
    No se puede eliminar a sí mismo.
    """
    # Validar que el usuario actual esté autenticado
    current_user = _get_current_user(db, token)
    
    # Verificar que el usuario actual sea admin
    _require_admin(current_user)
    
    # Buscar el usuario a eliminar
    target_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # No permitir que un admin se elimine a sí mismo
    if target_user.id_usuario == current_user.id_usuario:
        raise HTTPException(
            status_code=400,
            detail="No puede eliminarse a sí mismo"
        )
    
    # Guardar información antes de eliminar
    user_name = target_user.nombre
    user_email = target_user.correo
    
    # Eliminar el usuario
    db.delete(target_user)
    db.commit()
    
    return {
        "message": f"Usuario {user_name} ({user_email}) eliminado exitosamente",
        "usuario_id": user_id
    }
