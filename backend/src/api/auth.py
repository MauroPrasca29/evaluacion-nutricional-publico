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
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from db.session import get_db
from db.models import Usuario
from db.schemas import UsuarioCreate, UsuarioResponse

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


# ------------------------------------------------------------
# Registro
# ------------------------------------------------------------
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    """
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


@router.get("/me", response_model=MeResponse)
def me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = _get_current_user(db, token)
    return MeResponse(
        id_usuario=user.id_usuario,
        nombre=user.nombre,
        correo=user.correo,
        telefono=user.telefono,
    )
