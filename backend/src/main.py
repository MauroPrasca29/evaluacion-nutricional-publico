# FastAPI main entry point - empty file for structure

# FastAPI main application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Nutritional Assessment API",
    description="API for child nutritional assessment system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Nutritional Assessment API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# TODO: Include routers
from .api import auth, children, followups, reports, import_excel
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(children.router, prefix="/api/children", tags=["children"])
app.include_router(followups.router, prefix="/api/followups", tags=["followups"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(import_excel.router, prefix="/api/import", tags=["import"])
