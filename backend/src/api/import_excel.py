from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Este router se monta en main.py con prefix="/api/import"
# Rutas finales:
#   GET  /api/import/template
#   POST /api/import/excel
#   GET  /api/import/status/{import_id}
#   GET  /api/import/search
router = APIRouter(tags=["import"])

# Ruta al archivo de plantilla dentro del contenedor:
# /app/src/api/import_excel.py → parents[2] = /app
_BASE_DIR = Path(__file__).resolve().parents[2]
_TEMPLATE_PATH = _BASE_DIR / "data" / "plantilla_importacion.xlsx"


class ImportSummary(BaseModel):
    id: int
    filename: str
    status: str = Field(..., description="p.ej. processed / failed")
    total_rows: int
    created_children: int
    created_followups: int
    errors: List[str]
    created_at: datetime


# ----- Memoria temporal -----
_IMPORTS: Dict[int, Dict[str, Any]] = {}
_SEQ = 0


def _next_id() -> int:
    global _SEQ
    _SEQ += 1
    return _SEQ


def _to_summary(import_id: int, data: Dict[str, Any]) -> ImportSummary:
    return ImportSummary(
        id=import_id,
        filename=data.get("filename", ""),
        status=data.get("status", "processed"),
        total_rows=data.get("total_rows", 0),
        created_children=data.get("created_children", 0),
        created_followups=data.get("created_followups", 0),
        errors=list(data.get("errors", [])),
        created_at=data.get("created_at", datetime.utcnow()),
    )


# ----- Endpoints -----

@router.get("/template")
def get_template():
    """
    Devuelve la plantilla Excel de importación.

    Usa el archivo data/plantilla_importacion.xlsx que ya existe en el repo.
    """
    if not _TEMPLATE_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Template file not found on server",
        )

    return FileResponse(
        path=_TEMPLATE_PATH,
        filename="plantilla_importacion.xlsx",
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@router.post("/excel", response_model=ImportSummary)
async def import_excel(file: UploadFile = File(...)):
    """
    Registro de una importación en memoria.

    Modo diagnóstico:
    - NO escribe en base de datos.
    - NO parsea el Excel todavía.
    - Solo guarda un registro con contadores en 0.
    """
    import_id = _next_id()

    # En esta rama no procesamos el contenido real del archivo.
    # Solo lo leemos para vaciar el stream y lo descartamos.
    await file.read()

    data: Dict[str, Any] = {
        "filename": file.filename or f"import_{import_id}.xlsx",
        "status": "processed",
        "total_rows": 0,
        "created_children": 0,
        "created_followups": 0,
        "errors": [],
        "created_at": datetime.utcnow(),
    }
    _IMPORTS[import_id] = data

    return _to_summary(import_id, data)


@router.get("/status/{import_id}", response_model=ImportSummary)
def get_import_status(import_id: int):
    """
    Devuelve el resumen de una importación específica.
    """
    data = _IMPORTS.get(import_id)
    if not data:
        raise HTTPException(status_code=404, detail="Import not found")

    return _to_summary(import_id, data)


@router.get("/search", response_model=List[ImportSummary])
def search_imports(q: Optional[str] = Query(None, description="Filtro por nombre de archivo")):
    """
    Lista de importaciones registradas en memoria.
    Se puede filtrar por parte del nombre de archivo (q).
    """
    results: List[ImportSummary] = []
    for import_id, data in sorted(_IMPORTS.items(), key=lambda kv: kv[0]):
        filename = (data.get("filename") or "").lower()
        if q and q.lower() not in filename:
            continue
        results.append(_to_summary(import_id, data))
    return results
