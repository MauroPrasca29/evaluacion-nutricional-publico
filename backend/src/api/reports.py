from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["reports"])

class StatsResponse(BaseModel):
    total_children: int = Field(0, ge=0)
    active_alerts: int = Field(0, ge=0)
    pending_assessments: int = Field(0, ge=0)

class ExportResponse(BaseModel):
    message: str

class PDFResponse(BaseModel):
    message: str

@router.get("/statistics", response_model=StatsResponse)
def statistics():
    return StatsResponse(total_children=0, active_alerts=0, pending_assessments=0)

@router.get("/pdf/{child_id}", response_model=PDFResponse)
def pdf(child_id: int):
    return PDFResponse(message=f"Report for child {child_id} generated")

@router.post("/export", response_model=ExportResponse)
def export_data():
    return ExportResponse(message="Data exported successfully")

@router.get("/ping")
def ping():
    return {"ok": True, "service": "reports"}
