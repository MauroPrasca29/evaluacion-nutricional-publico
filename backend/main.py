"""
FastAPI main (modo dev, con BD en Railway)
- Carga condicional de settings y DB
- Registra routers desde src/api/*
- CORS y TrustedHost con defaults
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
from db_sistema_nutricion.app import models  # importa modelos

# --- Base inicial ---
app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend conectado a BD del sistema de nutrición"}

# --- Ajuste de path para src ---
sys.path.append(str(Path(__file__).parent / "src"))

# ---------- Settings opcionales ----------
try:
    from core.config import settings  # type: ignore
    ENV = getattr(settings, "ENVIRONMENT", "development")
    ALLOWED_HOSTS = getattr(settings, "ALLOWED_HOSTS", ["*"])
    ALLOWED_ORIGINS = getattr(settings, "ALLOWED_ORIGINS", ["*"])
except Exception:
    class _FallbackSettings:
        ENVIRONMENT = "development"
        ALLOWED_HOSTS = ["*"]
        ALLOWED_ORIGINS = ["*"]
    settings = _FallbackSettings()  # type: ignore
    ENV = settings.ENVIRONMENT
    ALLOWED_HOSTS = settings.ALLOWED_HOSTS
    ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("nutritional-api")

# ---------- Función para carga segura de routers ----------
def _try_import_router(mod_path: str, attr: str = "router"):
    try:
        mod = __import__(mod_path, fromlist=[attr])
        return getattr(mod, attr, None)
    except Exception as e:
        logger.error(f"No se pudo cargar el router '{mod_path}': {e}")
        return None

# ---------- Routers desde src/api ----------
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

# ---------- App ----------
app = FastAPI(
    title="Nutritional Assessment API",
    description="API para evaluación y seguimiento nutricional infantil",
    version="1.0.0",
    docs_url="/docs" if ENV == "development" else None,
    redoc_url="/redoc" if ENV == "development" else None,
    lifespan=lifespan,
)

# Seguridad de host (usar '*' en dev)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS if ALLOWED_HOSTS else ["*"]
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health ----------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "nutritional-assessment-api",
        "version": "1.0.0",
        "environment": ENV,
    }

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

# ---------- Manejadores globales ----------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found", "message": f"Resource not found: {request.url.path}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=(ENV == "development"),
        log_level="info",
    )
