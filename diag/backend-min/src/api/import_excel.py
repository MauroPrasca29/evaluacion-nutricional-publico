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
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    import openpyxl
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    # Datos de ejemplo
    data = [
        {
            "Tipo de documento": "CC",
            "Número de documento": "12345678",
            "Nombres": "NOMBRE",
            "Apellidos": "APELLIDO",
            "Género": "Femenino",  # Opciones: Femenino, Masculino
            "Fecha de nacimiento": "2015-01-01",
            "Talla (cm)": 120,
            "Peso (kg)": 23.5,
            "Pliegue subescapular (mm)": 8.0,
            "Perímetro cefálico (cm)": 48.5,
            "Pliegue cutáneo tricipital (mm)": 7.2,
            "Nivel de actividad": "Moderada",  # Opciones: Ligera, Moderada, Vigorosa
            "Tipo de alimentación": "Alimentados con leche materna",  # Opciones: Alimentados con leche materna, Alimentados con fórmula, Alimentados con leche materna + fórmula (todos), NA
            "Comentarios del cuidador": "Texto libre",
            "Notas": "Texto libre",
        }
    ]

    # Opciones para listas desplegables
    genero_opciones = ["Femenino", "Masculino"]
    alimentacion_opciones = [
        "Alimentados con leche materna",
        "Alimentados con fórmula",
        "Alimentados con leche materna + fórmula (todos)",
        "NA",
    ]
    actividad_opciones = ["Ligera", "Moderada", "Vigorosa"]

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Crear Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Plantilla")

    output.seek(0)
    wb = openpyxl.load_workbook(output)
    ws = wb.active

    # Ajustar ancho de columnas al texto
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except Exception:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[col_letter].width = adjusted_width

    # Agregar listas desplegables (validación de datos)
    # Buscar las columnas por nombre
    headers = [cell.value for cell in ws[1]]
    col_genero = headers.index("Género") + 1
    col_alimentacion = headers.index("Tipo de alimentación") + 1
    col_actividad = headers.index("Nivel de actividad") + 1

    # Rango de filas (desde la segunda hasta la 100 por defecto)
    max_row = 100

    # Género
    dv_genero = DataValidation(
        type="list",
        formula1='"{}"'.format(",".join(genero_opciones)),
        showErrorMessage=True,
        errorTitle="Valor inválido",
        error="Solo puedes seleccionar uno de los valores de la lista.",

    )
    ws.add_data_validation(dv_genero)
    dv_genero.add(f"{get_column_letter(col_genero)}2:{get_column_letter(col_genero)}{max_row}")
    # Tipo de alimentación
    dv_alimentacion = DataValidation(
        type="list",
        formula1='"{}"'.format(",".join(alimentacion_opciones)),
        showErrorMessage=True,
        errorTitle="Valor inválido",
        error="Solo puedes seleccionar uno de los valores de la lista.",

    )
    ws.add_data_validation(dv_alimentacion)
    dv_alimentacion.add(f"{get_column_letter(col_alimentacion)}2:{get_column_letter(col_alimentacion)}{max_row}")

    # Nivel de actividad
    dv_actividad = DataValidation(
        type="list",
        formula1='"{}"'.format(",".join(actividad_opciones)),
        showErrorMessage=True,
        errorTitle="Valor inválido",
        error="Solo puedes seleccionar uno de los valores de la lista.",

    )
    ws.add_data_validation(dv_actividad)
    dv_actividad.add(f"{get_column_letter(col_actividad)}2:{get_column_letter(col_actividad)}{max_row}")

    # Guardar el archivo ajustado en memoria
    final_output = io.BytesIO()
    wb.save(final_output)
    final_output.seek(0)

    headers = {"Content-Disposition": 'attachment; filename="plantilla_importacion.xlsx"'}
    return StreamingResponse(
        final_output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

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
