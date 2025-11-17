from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging
import os
import sys
import subprocess

from src.api import auth as auth_router
from src.api import children as children_router
from src.api import followups as followups_router
from src.api import reports as reports_router
from src.api import import_excel as import_router
from src.api import nutrition as nutrition_router
from src.api import vision_anemia_onnx as anemia_router
from src.api import sedes as sedes_router
from src.api import acudientes as acudientes_router


logger = logging.getLogger("nutritional-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# ===== DESCARGA AUTOMÁTICA DE MODELOS ONNX =====
def ensure_anemia_models():
    """Verifica y descarga modelos ONNX si no existen."""
    models_dir = os.path.join(os.getcwd(), "models")
    required_models = [
        "hb_regressor_infants_ft.onnx",
        "hb_regressor_infants_ft.pth"
    ]
    
    missing_models = [m for m in required_models if not os.path.exists(os.path.join(models_dir, m))]
    
    if missing_models:
        logger.warning(f"⚠️  Modelos faltantes: {missing_models}")
        logger.info("📥 Intentando descargar modelos ONNX...")
        
        # Ubicación del script de descarga
        download_script = os.path.join(os.path.dirname(__file__), "..", "scripts", "download_models.py")
        
        if os.path.exists(download_script):
            try:
                result = subprocess.run(
                    [sys.executable, download_script, "--models-dir", models_dir],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutos máximo
                )
                logger.info(result.stdout)
                if result.returncode != 0:
                    logger.error(f"❌ Error descargando modelos: {result.stderr}")
                else:
                    logger.info("✅ Modelos descargados exitosamente.")
            except subprocess.TimeoutExpired:
                logger.error("❌ Timeout descargando modelos. Continuar sin modelos.")
            except Exception as e:
                logger.error(f"❌ Error ejecutando script de descarga: {e}")
        else:
            logger.warning(f"⚠️  Script de descarga no encontrado en {download_script}")
    else:
        logger.info(f"✅ Todos los modelos ONNX están presentes.")

# Ejecutar descarga de modelos antes de crear la app
ensure_anemia_models()

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
logger.info("Router cargado: api.nutrition")

app.include_router(anemia_router.router, prefix="/api/vision")
logger.info("Router cargado: api.vision_anemia_onnx")

app.include_router(sedes_router.router, prefix="/api/sedes")
logger.info("Router cargado: api.sedes")

app.include_router(acudientes_router.router, prefix="/api/acudientes")
logger.info("Router cargado: api.acudientes")
