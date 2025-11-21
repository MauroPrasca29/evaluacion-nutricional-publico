# backend/src/api/import_excel.py
# Servicio de importación de Excel con "vector store" ligero (TF-IDF).
# Rutas:
#   POST /import/excel            -> subir Excel, vectorizar y persistir (devuelve import_id)
#   GET  /import/template         -> descargar plantilla Excel
#   GET  /import/status/{id}      -> consultar estado del import
#   GET  /import/search           -> búsqueda por similitud (coseno) dentro de un import_id

from __future__ import annotations

import io
import json
import os
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.services.activity_service import ActivityService


# --------------------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------------------
router = APIRouter(tags=["Importación Excel"])  # <- aparecerá agrupado en /docs

DATA_DIR = os.getenv("VECTOR_DATA_DIR", "./data/imports")  # carpeta base de persistencia
os.makedirs(DATA_DIR, exist_ok=True)
ALLOWED_EXTS = (".xlsx", ".xls")


# --------------------------------------------------------------------------------------
# Modelos
# --------------------------------------------------------------------------------------
class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportMeta(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    import_id: str
    filename: str
    created_at: float
    status: ImportStatus
    rows: int = 0
    message: Optional[str] = None


class SearchResult(BaseModel):
    row_index: int
    score: float
    payload: Dict[str, str]


# --------------------------------------------------------------------------------------
# VectorStore (persistencia simple por import_id)
# --------------------------------------------------------------------------------------
class VectorStore:
    """
    "Vector DB" simple por import_id.
    Persiste: vocab.json, matrix.npz, payload.json, meta.json
    """

    def __init__(self, import_id: str):
        self.import_id = import_id
        self.base = os.path.join(DATA_DIR, import_id)
        self.meta_path = os.path.join(self.base, "meta.json")
        self.vocab_path = os.path.join(self.base, "vocab.json")
        self.matrix_path = os.path.join(self.base, "matrix.npz")
        self.payload_path = os.path.join(self.base, "payload.json")
        os.makedirs(self.base, exist_ok=True)

        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix = None  # scipy.sparse o ndarray
        self.payloads: List[Dict[str, str]] = []

    def save(self, vectorizer: TfidfVectorizer, matrix, payloads: List[Dict[str, str]]):
        self.vectorizer = vectorizer
        self.matrix = matrix
        self.payloads = payloads

        # Guardar vocabulario + idf + config
        with open(self.vocab_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "vocabulary_": vectorizer.vocabulary_,
                    "idf_": vectorizer.idf_.tolist(),
                    "lowercase": vectorizer.lowercase,
                    "ngram_range": vectorizer.ngram_range,
                    "norm": vectorizer.norm,
                },
                f,
                ensure_ascii=False,
            )

        # Guardar matriz
        try:
            from scipy import sparse  # opcional (si está instalado)

            if sparse.issparse(matrix):
                sparse.save_npz(self.matrix_path, matrix)
            else:
                np.savez_compressed(self.matrix_path, matrix=matrix)
        except Exception:
            arr = matrix.toarray() if hasattr(matrix, "toarray") else np.asarray(matrix)
            np.savez_compressed(self.matrix_path, matrix=arr)

        # Guardar payloads (filas originales)
        with open(self.payload_path, "w", encoding="utf-8") as f:
            json.dump(payloads, f, ensure_ascii=False)

    def load(self) -> bool:
        if not (os.path.exists(self.vocab_path) and os.path.exists(self.matrix_path) and os.path.exists(self.payload_path)):
            return False

        with open(self.vocab_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        vec = TfidfVectorizer(
            lowercase=data.get("lowercase", True),
            ngram_range=tuple(data.get("ngram_range", (1, 1))),
            norm=data.get("norm", "l2"),
        )
        vec.vocabulary_ = {k: int(v) for k, v in data["vocabulary_"].items()}
        vec.idf_ = np.array(data["idf_"])
        vec._tfidf._idf_diag = None
        self.vectorizer = vec

        try:
            from scipy import sparse
            try:
                self.matrix = sparse.load_npz(self.matrix_path)
            except Exception:
                arr = np.load(self.matrix_path)["matrix"]
                self.matrix = sparse.csr_matrix(arr)
        except Exception:
            arr = np.load(self.matrix_path)["matrix"]
            self.matrix = arr

        with open(self.payload_path, "r", encoding="utf-8") as f:
            self.payloads = json.load(f)

        return True

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        if not self.vectorizer or self.matrix is None:
            raise RuntimeError("Vector store no cargado")
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).ravel()
        top_idx = np.argsort(-sims)[: max(1, top_k)]
        return [(int(i), float(sims[i])) for i in top_idx]


# --------------------------------------------------------------------------------------
# Estado en memoria + helpers
# --------------------------------------------------------------------------------------
IMPORTS: Dict[str, ImportMeta] = {}


def _load_or_init_meta(import_id: str, filename: str) -> ImportMeta:
    base = os.path.join(DATA_DIR, import_id)
    os.makedirs(base, exist_ok=True)
    meta_path = os.path.join(base, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = ImportMeta(**json.load(f))
    else:
        meta = ImportMeta(
            import_id=import_id,
            filename=filename,
            created_at=time.time(),
            status=ImportStatus.PENDING,
        )
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta.model_dump(), f, ensure_ascii=False)
    IMPORTS[import_id] = meta
    return meta


def _set_status(import_id: str, status: ImportStatus, message: Optional[str] = None, rows: int = 0):
    meta = IMPORTS.get(import_id)
    if not meta:
        return
    meta.status = status
    meta.message = message
    if rows:
        meta.rows = rows
    base = os.path.join(DATA_DIR, import_id)
    meta_path = os.path.join(base, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta.model_dump(), f, ensure_ascii=False)


def dataframe_to_texts(df: pd.DataFrame, text_columns: Optional[List[str]] = None) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Convierte cada fila del DataFrame en texto:
    - Si text_columns es None, concatena todas las columnas no vacías.
    """
    texts: List[str] = []
    payloads: List[Dict[str, str]] = []

    if text_columns:
        missing = [c for c in text_columns if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Columnas no encontradas en Excel: {missing}")

    for _, row in df.iterrows():
        row_dict = {str(k): "" if pd.isna(v) else str(v) for k, v in row.to_dict().items()}
        parts = [row_dict.get(col, "") for col in text_columns] if text_columns else [v for v in row_dict.values() if str(v).strip()]
        text = " | ".join([p.strip() for p in parts if p and p.strip()])
        texts.append(text if text else "(fila vacía)")
        payloads.append(row_dict)

    return texts, payloads


def fit_tfidf(texts: List[str]) -> Tuple[TfidfVectorizer, any]:
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), norm="l2")
    mat = vec.fit_transform(texts)
    return vec, mat


# --------------------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------------------
@router.post("/excel", summary="Importar Excel (vectoriza y persiste por import_id)")
async def import_excel_file(
    file: UploadFile = File(...),
    text_columns: Optional[str] = Query(
        default=None,
        description="CSV de columnas a usar como texto. Si omites, concatena todas.",
    ),
) -> JSONResponse:
    filename = (file.filename or "").strip()
    if not filename or not filename.lower().endswith(ALLOWED_EXTS):
        raise HTTPException(status_code=400, detail="Invalid file format. Use .xlsx o .xls")

    import_id = str(uuid.uuid4())
    _load_or_init_meta(import_id, filename)
    _set_status(import_id, ImportStatus.PROCESSING, "Leyendo Excel...")

    try:
        content = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            _set_status(import_id, ImportStatus.FAILED, f"No se pudo leer el Excel: {e}")
            raise HTTPException(status_code=400, detail=f"No se pudo leer el Excel: {e}")

        if df.empty:
            _set_status(import_id, ImportStatus.FAILED, "El Excel no contiene filas")
            raise HTTPException(status_code=400, detail="El Excel no contiene filas")

        # limpiar columnas Unnamed generadas por Excel
        cols = [c for c in df.columns if not str(c).startswith("Unnamed")]
        df = df[cols] if cols else df

        cols_arg = [c.strip() for c in text_columns.split(",")] if text_columns else None
        texts, payloads = dataframe_to_texts(df, cols_arg)

        _set_status(import_id, ImportStatus.PROCESSING, "Vectorizando...")
        vectorizer, matrix = fit_tfidf(texts)

        store = VectorStore(import_id)
        store.save(vectorizer, matrix, payloads)

        _set_status(import_id, ImportStatus.COMPLETED, "Import finalizado", rows=len(payloads))
        return JSONResponse(
            status_code=200,
            content={
                "import_id": import_id,
                "filename": filename,
                "rows": len(payloads),
                "status": ImportStatus.COMPLETED,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        _set_status(import_id, ImportStatus.FAILED, f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


@router.get("/template", summary="Descargar plantilla Excel")
async def download_template():
    """Descargar plantilla Excel con todas las columnas necesarias"""
    from src.services.excel_service import ExcelService
    
    try:
        # Usar el servicio actualizado para generar la plantilla
        excel_bytes = ExcelService.generate_template()
        
        # Crear respuesta con el archivo
        output = io.BytesIO(excel_bytes)
        output.seek(0)
        
        headers = {"Content-Disposition": 'attachment; filename="plantilla_importacion_completa.xlsx"'}
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar plantilla: {str(e)}")

import time as time_module

@router.post("/upload", summary="Cargar Excel e insertar infantes y seguimientos")
async def upload_children_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Procesa un archivo Excel con datos de infantes, acudientes y seguimientos.
    Valida cada fila, crea/busca acudientes e infantes, y genera seguimientos con evaluaciones nutricionales.
    """
    filename = (file.filename or "").strip()
    if not filename or not filename.lower().endswith(ALLOWED_EXTS):
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Use .xlsx o .xls")

    # ⏱️ Iniciar contador de tiempo
    start_time = time_module.time()
    
    try:
        print(f"📥 Recibiendo archivo: {filename}")
        
        # Leer contenido del archivo
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        print(f"📊 Tamaño del archivo: {file_size_mb:.2f} MB")
        
        # Procesar con ExcelService
        from src.services.excel_service import ExcelService
        
        print(f"⚙️ Iniciando procesamiento con ExcelService...")
        processing_start = time_module.time()
        
        result = ExcelService.process_children_excel(content, db)
        
        processing_time = time_module.time() - processing_start
        print(f"✅ Procesamiento completado en {processing_time:.2f} segundos")
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Error al procesar el archivo"))
        
        # Después de procesar el Excel - registrar actividad
        sede_nombre = "Importación Excel"
        if result.get("data") and len(result["data"]) > 0:
            # Intentar obtener sede_id del primer registro procesado
            primer_registro = result["data"][0]
            sede_id = primer_registro.get("sede_id")
            if sede_id:
                from src.db.models import Sede
                sede = db.query(Sede).filter(Sede.id_sede == sede_id).first()
                if sede:
                    sede_nombre = sede.nombre

        print(f"📝 Registrando actividad en el sistema...")
        ActivityService.registrar_importacion(
            db=db,
            sede_nombre=sede_nombre,
            cantidad=result.get("processed_count", 0),
            usuario_id=1  # TODO: Obtener del token JWT
        )
        
        # ⏱️ Calcular tiempo total
        total_time = time_module.time() - start_time
        print(f"🎉 Importación completada exitosamente en {total_time:.2f} segundos")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "total_rows": result.get("total_rows", 0),
                "processed_count": result.get("processed_count", 0),
                "error_count": result.get("error_count", 0),
                "errors": result.get("errors", []),
                "data": result.get("data", []),
                "processing_time": round(total_time, 2)  # ⏱️ Agregar tiempo de procesamiento
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time_module.time() - start_time
        print(f"❌ Error después de {elapsed:.2f} segundos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error inesperado al procesar el archivo: {str(e)}")

@router.get("/status/{import_id}", summary="Consultar estado de import")
async def get_import_status(import_id: str):
    meta = IMPORTS.get(import_id)
    if not meta:
        base = os.path.join(DATA_DIR, import_id)
        meta_path = os.path.join(base, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = ImportMeta(**json.load(f))
            IMPORTS[import_id] = meta
        else:
            raise HTTPException(status_code=404, detail="import_id no encontrado")
    return JSONResponse(status_code=200, content=meta.model_dump())


@router.get("/search", summary="Buscar por similitud en un import_id")
async def search_in_import(
    import_id: str = Query(..., description="ID devuelto por /import/excel"),
    q: str = Query(..., description="Consulta de texto"),
    top_k: int = Query(5, ge=1, le=50),
) -> List[SearchResult]:
    store = VectorStore(import_id)
    if not store.load():
        raise HTTPException(status_code=404, detail="No existe vector store para ese import_id")
    results = store.search(q, top_k=top_k)

    return [SearchResult(row_index=i, score=s, payload=store.payloads[i]) for i, s in results]
