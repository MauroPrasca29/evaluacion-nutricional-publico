from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib
import logging

from src.api import auth as auth_router
from src.api import children as children_router
from src.api import followups as followups_router
from src.api import reports as reports_router
from src.api import import_excel as import_router

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
