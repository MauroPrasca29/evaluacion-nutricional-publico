from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging

from src.api import auth as auth_router
from src.api import children as children_router
from src.api import followups as followups_router
from src.api import reports as reports_router
from src.api import import_excel as import_router
from src.api import nutrition as nutrition_router
from src.db.session import SessionLocal
from src.db.models import Usuario, Rol
from core.security import get_password_hash
import os


logger = logging.getLogger("nutritional-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="Nutritional Assessment API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def root():
    return {"ok": True}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/healthz")
def healthz():
    return {"ok": True}

# Routers (OJO: los módulos NO llevan prefix; el prefix se define aquí)
app.include_router(auth_router.router, prefix="/api/auth")
logger.info("Router cargado: api.auth")

app.include_router(children_router.router, prefix="/api/children")
logger.info("Router cargado: api.children")

app.include_router(followups_router.router, prefix="/api/followups")
logger.info("Router cargado: api.followups")

app.include_router(reports_router.router, prefix="/api/reports")
logger.info("Router cargado: api.reports")

app.include_router(import_router.router, prefix="/api/import")
logger.info("Router cargado: api.import_excel")

app.include_router(nutrition_router.router, prefix="/api/nutrition")


@app.on_event("startup")
def ensure_admin_user():
    """Ensure there is at least one admin user with a usable password.
    If a seeded admin has a placeholder password like 'hashed_password_admin', replace it
    with a bcrypt hash generated from ENV `ADMIN_PASSWORD` (defaults to 'admin123').
    """
    db = SessionLocal()
    try:
        # Ensure the admin role exists
        admin_role = db.query(Rol).filter(Rol.nombre.ilike("administrador")).first()
        if not admin_role:
            admin_role = Rol(nombre="Administrador", descripcion="Rol administrador creado en startup")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        # Find any user assigned to admin role
        admin_user = db.query(Usuario).filter(Usuario.rol_id == admin_role.id_rol).first()
        if not admin_user:
            pwd = os.getenv("ADMIN_PASSWORD", "admin123")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            admin_phone = os.getenv("ADMIN_PHONE", "3000000000")
            admin_user = Usuario(
                nombre="Administrador",
                correo=admin_email,
                telefono=admin_phone,
                contrasena=get_password_hash(pwd),
                rol_id=admin_role.id_rol,
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Admin creado: {admin_email}")
        else:
            # If seeded password is a placeholder, replace it
            if isinstance(admin_user.contrasena, str) and admin_user.contrasena.startswith("hashed_password"):
                pwd = os.getenv("ADMIN_PASSWORD", "admin123")
                admin_user.contrasena = get_password_hash(pwd)
                db.commit()
                print("🔐 Contraseña del admin actualizada desde placeholder")
    except Exception as e:
        print("⚠️ Error al asegurar admin:", e)
    finally:
        try:
            db.close()
        except Exception:
            pass
