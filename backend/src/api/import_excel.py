from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter(tags=["import"])

class ImportStatusResponse(BaseModel):
    import_id: str
    status: str

class MessageResponse(BaseModel):
    message: str

@router.post("/excel", response_model=MessageResponse)
async def upload_excel(file: UploadFile = File(...)):
    _ = await file.read()
    return MessageResponse(message=f"File {file.filename} processed successfully")

@router.get("/template", response_model=MessageResponse)
def download_template():
    return MessageResponse(message="Template download endpoint")

@router.get("/status/{import_id}", response_model=ImportStatusResponse)
def import_status(import_id: str):
    return ImportStatusResponse(import_id=import_id, status="completed")

@router.get("/ping")
def ping():
    return {"ok": True, "service": "import"}
