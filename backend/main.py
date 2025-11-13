"""
FastAPI main (modo dev, con DB opcional) para el Sistema de Evaluación Nutricional
- Ajusta sys.path para encontrar /app/src (imports de api.* y src.api.*)
- Carga condicional de settings y DB
- Registra routers: children, auth, followups, reports, import_excel
- CORS y TrustedHost configurados dinámicamente
- Incluye healthcheck para Docker (/health y /healthz)
"""

from contextlib import asynccontextmanager
from pathlib import Path
import importlib
import logging
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text  # para testear la conexión SQL

# --- Configuración de imports ---
HERE = Path(__file__).parent.resolve()
SRC_DIR = (HERE / "src").resolve()

# Garantiza que Python vea /app y /app/src
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))
# Prioridad alta para /app/src
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ---------- Settings ----------
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
    # correremos sin DB si no está disponible
    pass

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("nutritional-api")

# ---------- Cargar routers ----------
def _try_import_router(candidates, attr: str = "router"):
    """
    Intenta importar un router probando una lista de módulos.
    Registra logs de éxito/fracaso y devuelve el router si lo encuentra.
    """
    for mod_path in candidates:
        try:
            mod = importlib.import_module(mod_path)
            r = getattr(mod, attr, None)
            if r:
                logger.info(f"Router cargado: {mod_path}")
                return r
            else:
                logger.warning(f"Módulo {mod_path} importado pero no expone '{attr}'")
        except Exception as e:
            logger.warning(f"No se pudo cargar router {mod_path}: {e}")
    return None

# Routers principales (intentando api.* y src.api.*)
children_router     = _try_import_router(["api.children", "src.api.children"])
auth_router         = _try_import_router(["api.auth", "src.api.auth"])
followups_router    = _try_import_router(["api.followups", "src.api.followups"])
reports_router      = _try_import_router(["api.reports", "src.api.reports"])
import_excel_router = _try_import_router(["api.import_excel", "src.api.import_excel"])
nutrition_router    = _try_import_router(["api.nutrition", "src.api.nutrition"])

# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Nutritional Assessment API...")
    # Crear tablas si hay DB
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

# ---------- Middleware ----------
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS if ALLOWED_HOSTS else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Endpoints base ----------
@app.get("/health")
async def health_check():
    """
    Verifica el estado general y la conexión con la base de datos.
    No rompe el health si la DB falla; reporta 'degraded'.
    """
    db_ok = False
    db_error: str | None = None

    if _SessionLocal:
        try:
            db = _SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_ok = True
        except Exception as e:
            db_error = str(e)
            logger.error(f"Health check failed: {e}")

    status = "healthy" if db_ok else "degraded"

    return {
        "status": status,
        "service": "nutritional-assessment-api",
        "version": "1.0.0",
        "environment": ENV,
        "db": db_ok,
        "db_error": db_error,
    }


@app.get("/healthz")
async def healthz_check():
    """Alias para Docker healthcheck"""
    return await health_check()


@app.get("/")
async def root():
    """Endpoint raíz informativo"""
    return {
        "message": "Nutritional Assessment API",
        "version": "1.0.0",
        "docs": "/docs" if ENV == "development" else "Documentation disabled in production",
        "health": "/health",
    }

# ---------- Registro de routers ----------
if children_router:
    app.include_router(children_router, prefix="/api/children", tags=["children"])
if auth_router:
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
if followups_router:
    app.include_router(followups_router, prefix="/api/followups", tags=["followups"])
if reports_router:
    app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
if import_excel_router:
    app.include_router(import_excel_router, prefix="/api/import", tags=["import"])
if nutrition_router:
    app.include_router(nutrition_router, prefix="/api/nutrition", tags=["nutrition"])


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

# ---------- Main ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=(ENV == "development"),
        log_level="info",
    )
