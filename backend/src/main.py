<<<<<<< HEAD
"""
FastAPI main (modo dev, con BD en Railway)
- Registra routers desde src/api/*
"""

from contextlib import asynccontextmanager
from pathlib import Path
import logging
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from db_sistema_nutricion.app.models import engine, Base
from db_sistema_nutricion.app import models

# --- Configuración inicial ---
app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend conectado a BD del sistema de nutrición"}

# --- Agregar /src al path de Python ---
sys.path.append(str(Path(__file__).parent / "src"))

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging

from src.api import auth as auth_router
from src.api import children as children_router
from src.api import followups as followups_router
from src.api import reports as reports_router
from src.api import import_excel as import_router

>>>>>>> fusion-kaleth
logger = logging.getLogger("nutritional-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

<<<<<<< HEAD
# ---------- Carga dinámica de routers ----------
def _try_import_router(mod_path: str, attr: str = "router"):
    try:
        mod = __import__(mod_path, fromlist=[attr])
        return getattr(mod, attr, None)
    except Exception as e:
        logger.error(f"No se pudo cargar el router '{mod_path}': {e}")
        return None

# ✅ Cambiar imports de "api" → "src.api"
children_router = _try_import_router("src.api.children")
followups_router = _try_import_router("src.api.followups")
reports_router = _try_import_router("src.api.reports")
import_excel_router = _try_import_router("src.api.import_excel")
auth_router = _try_import_router("src.api.auth")

# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Nutritional Assessment API...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Apagando Nutritional Assessment API...")

# ---------- FastAPI principal ----------
app = FastAPI(
    title="Nutritional Assessment API",
    description="API para evaluación y seguimiento nutricional infantil",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------- Middleware ----------
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
=======
app = FastAPI(
    title="Nutritional Assessment API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
>>>>>>> fusion-kaleth
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

<<<<<<< HEAD
# ---------- Health ----------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nutritional-assessment-api"}

# ---------- Registro de routers ----------
if children_router:
    app.include_router(children_router, prefix="/api/children", tags=["children"])
if followups_router:
    app.include_router(followups_router, prefix="/api/followups", tags=["followups"])
if reports_router:
    app.include_router(reports_router, prefix="/api/reports")
if import_excel_router:
    app.include_router(import_excel_router, prefix="/api/import")
if auth_router:
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# ---------- Excepciones ----------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
=======
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
>>>>>>> fusion-kaleth
