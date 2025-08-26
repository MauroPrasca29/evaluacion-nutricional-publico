"""
FastAPI main application for Nutritional Assessment System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Nutritional Assessment API",
    description="API for managing child nutritional assessments and health monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "service": "nutritional-assessment-api",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Nutritional Assessment API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# API endpoints
@app.get("/api/children")
async def get_children():
    """Get all children"""
    return {"children": []}

@app.get("/api/followups")
async def get_followups():
    """Get all followups"""
    return {"followups": []}

@app.get("/api/reports")
async def get_reports():
    """Get all reports"""
    return {"reports": []}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
