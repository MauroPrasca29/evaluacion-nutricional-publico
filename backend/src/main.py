"""
FastAPI main entry point for Nutritional Assessment API
-------------------------------------------------------
Compatible with local Docker & Railway environments.
Loads routers from src/api and database from src/db.
"""

# ===============================================
# Autor: Mauro Prasca T00065353
# ===============================================

from contextlib import asynccontextmanager
from pathlib import Path
import logging
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

# --- Ajuste de sys.path ---
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("nutritional-api")

# ---------- Settings ----------
try:
    from core.config import settings  # type: ignore
    ENV = getattr(settings, "ENVIRONMENT", "development")
    ALLOWED_HOSTS = getattr(settings, "ALLOWED_HOSTS", ["*"])
    ALLOWED_ORIGINS = getattr(settings, "ALLOWED_ORIGINS", ["*"])
    logger.info(f"✅ Loaded config for environment: {ENV}")
except Exception as e:
    logger.warning(f"⚠️ Using fallback settings: {e}")

    class _FallbackSettings:
        ENVIRONMENT = "development"
        ALLOWED_HOSTS = ["*"]
        ALLOWED_ORIGINS = ["*"]

    settings = _FallbackSettings()
    ENV = settings.ENVIRONMENT
    ALLOWED_HOSTS = settings.ALLOWED_HOSTS
    ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS

# ---------- Database ----------
_engine = None
_SessionLocal = None
_Base = None

try:
    from db.session import engine as _engine, SessionLocal as _SessionLocal  # type: ignore
    from db.base import Base as _Base  # type: ignore
    logger.info("✅ Database loaded from db")
except Exception:
    try:
        from src.db.session import engine as _engine, SessionLocal as _SessionLocal  # type: ignore
        from src.db.base import Base as _Base  # type: ignore
        logger.info("✅ Database loaded from src.db")
    except Exception as e:
        logger.error(f"❌ Could not import DB modules: {e}")

# ---------- Routers ----------
def _try_import_router(mod_path: str, attr: str = "router"):
    try:
        mod = __import__(mod_path, fromlist=[attr])
        r = getattr(mod, attr, None)
        if r:
            logger.info(f"✅ Loaded router: {mod_path}")
            return r
    except Exception as e:
        logger.warning(f"⚠️ Could not load router {mod_path}: {e}")
    return None

# Load routers
children_router = _try_import_router("src.api.children")
auth_router = _try_import_router("src.api.auth")
followups_router = _try_import_router("src.api.followups")
reports_router = _try_import_router("src.api.reports")
import_excel_router = _try_import_router("src.api.import_excel")

# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Nutritional Assessment API...")
    if _engine and _Base:
        try:
            _Base.metadata.create_all(bind=_engine)
            logger.info("✅ Tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
    yield
    logger.info("🛑 Shutting down Nutritional Assessment API...")

# ---------- App ----------
app = FastAPI(
    title="Nutritional Assessment API",
    description="API para evaluación y seguimiento nutricional infantil",
    version="1.0.0",
    docs_url="/docs" if ENV == "development" else None,
    redoc_url="/redoc" if ENV == "development" else None,
    lifespan=lifespan,
)

# ---------- Middlewares ----------
app.add_middl_
