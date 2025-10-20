# src/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.db.session import get_db
from src.db.models import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Contexto de hash seguro (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------
# Schemas
# ---------------------------
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


# ---------------------------
# Utilidades
# ---------------------------
def get_password_hash(password: str) -> str:
    """Genera hash seguro para contraseñas (máx 72 bytes para bcrypt)."""
    if not isinstance(password, str):
        raise ValueError("Password debe ser texto plano")
    password = password.strip()
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------
# Rutas
# ---------------------------

@router.post("/register", status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Validar si el usuario o email ya existen
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya está registrado")

    # Crear hash seguro de la contraseña
    hashed_password = get_password_hash(user.password)

    # Crear usuario
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User '{new_user.username}' registered successfully"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "access_token": f"fake-jwt-token-for-{user.username}",
        "token_type": "bearer"
    }


@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Ejemplo de respuesta fake
    return {
        "username": "test_user",
        "email": "test@example.com"
    }
