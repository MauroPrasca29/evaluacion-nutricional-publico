"""
FastAPI main (modo dev, sin DB obligatoria) para el Sistema de Evaluación Nutricional
- Carga condicional de settings y DB
- Registra routers `children`, `followups`, `reports`, `import_excel`, `auth`
- CORS y TrustedHost con defaults si no hay settings
"""
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# --- Prep ruta para imports absolutos (api/*) ---
sys.path.append(str(Path(__file__).parent))

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

# ---------- DB opcional ----------
_engine = None
_SessionLocal = None
_Base = None
try:
    from db.session import engine as _engine, SessionLocal as _SessionLocal  # type: ignore
    from db.base import Base as _Base  # type: ignore
except Exception:
    pass  # correremos sin DB

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

# ---------- Routers ----------
children_router = _try_import_router("api.children")
followups_router = _try_import_router("api.followups")
reports_router = _try_import_router("api.reports")
import_excel_router = _try_import_router("api.import_excel")
auth_router = _try_import_router("api.auth")

# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Nutritional Assessment API...")
    if _engine and _Base:
        try:
            _Base.metadata.create_all(bind=_engine)
            logger.info("Tablas creadas OK")
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
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
    try:
        if _SessionLocal:
            db = _SessionLocal()
            db.execute("SELECT 1")
            db.close()
        return {
            "status": "healthy",
            "service": "nutritional-assessment-api",
            "version": "1.0.0",
            "environment": ENV,
            "db": bool(_SessionLocal),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/")
async def root():
    return {
        "message": "Nutritional Assessment API",
        "version": "1.0.0",
        "docs": "/docs" if ENV == "development" else "Documentation disabled in production",
        "health": "/health",
    }

# ---------- Registro de routers ----------
if children_router:
    app.include_router(children_router, prefix="/api/children", tags=["children"])

if followups_router:
    app.include_router(followups_router, prefix="/api/followups", tags=["followups"])

if reports_router:
    app.include_router(reports_router, prefix="/api/reports")  # tags ya están en reports.py

if import_excel_router:
    app.include_router(import_excel_router, prefix="/api/import")  # tags ya están en import_excel.py

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
