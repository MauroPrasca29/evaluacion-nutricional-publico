"""
FastAPI main application for Nutritional Assessment System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging, sys

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("nutritional-assessment-api")

# ---------------- App (crear UNA sola vez) ----------------
app = FastAPI(
    title="Nutritional Assessment API",
    description="API for managing child nutritional assessments and health monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    # En dev puedes dejar "*" o restringir a GitHub Codespaces con allow_origin_regex
    allow_origins=["*"],
    # allow_origin_regex=r"https://.*\.github\.dev$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routers ----------------
# Importación de Excel
from src.api.import_excel import router as import_excel_router
app.include_router(import_excel_router, prefix="/import", tags=["Importación Excel"])

# Reports (usa datos del import_id)
from src.api.reports import router as reports_router
app.include_router(reports_router)

# ---------------- Endpoints base ----------------
@app.get("/health", summary="Health check")
async def health_check():
    return {
        "status": "healthy",
        "service": "nutritional-assessment-api",
        "version": "1.0.0",
    }

@app.get("/", summary="Root")
async def root():
    return {
        "message": "Nutritional Assessment API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

# (Placeholders de ejemplo: puedes eliminarlos si no los usas)
@app.get("/api/children", summary="Get Children")
async def get_children():
    return {"children": []}

@app.get("/api/followups", summary="Get Followups")
async def get_followups():
    return {"followups": []}

# ---------------- Global exception handler ----------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": "An unexpected error occurred"},
    )

# ---------------- Local run ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
