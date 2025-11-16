# vision_anemia_onnx.py
# Módulo para detección de anemia usando ONNX Runtime

import io
import os
import uuid
import tempfile
import numpy as np
import cv2
import onnxruntime as ort
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

# Celery (opcional)
ANEMIA_ASYNC = os.getenv("ANEMIA_ASYNC", "false").lower() in ("1", "true", "yes")
if ANEMIA_ASYNC:
    try:
        # importa la app de Celery
        from tasks.anemia_tasks import infer_anemia
        from tasks.celery_app import celery as celery_app
    except Exception as e:
        # si falla la importación, no abortamos; lanzaremos error al intentar usar async
        infer_anemia = None
        celery_app = None
from PIL import Image, UnidentifiedImageError

# Importar funciones de inferencia desde el módulo core para evitar import
# circular con las tareas
from src.api.vision_anemia_core import predict_hb_from_bytes, threshold_by_age

# Crear router para integrarse con el backend principal
router = APIRouter()

# ---------- CONFIG BÁSICA ----------

# Intentar diferentes rutas posibles para el modelo
POSSIBLE_PATHS = [
    "models/hb_regressor_infants_ft.onnx",  # Ruta relativa desde /app
    "/app/models/hb_regressor_infants_ft.onnx",  # Ruta absoluta en Docker
    "./models/hb_regressor_infants_ft.onnx",  # Ruta relativa actual
]

MODEL_PATH = os.getenv("ANEMIA_ONNX_PATH", None)

if not MODEL_PATH:
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            MODEL_PATH = path
            break

if not MODEL_PATH:
    raise RuntimeError(f"No se encontró el modelo ONNX. Intenté: {POSSIBLE_PATHS}")

print(f"🔍 Usando modelo ONNX: {MODEL_PATH}")

# umbrales ajustados que encontraste en el notebook
OFFSET_SMALL = 1.00   # 6–59 meses
OFFSET_BIG   = 0.75   # 60–131 meses

# Validación de uploads
MAX_FILE_SIZE = int(os.getenv("ANEMIA_MAX_FILE_SIZE", 5 * 1024 * 1024))  # 5 MB por defecto
ALLOWED_MIME = {"image/jpeg", "image/png"}
ALLOWED_EXT = {".jpg", ".jpeg", ".png"}
UPLOAD_DIR = os.getenv("ANEMIA_UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
# Limpieza automática
ENABLE_UPLOAD_CLEANUP = os.getenv("ANEMIA_ENABLE_UPLOAD_CLEANUP", "true").lower() in ("1", "true", "yes")
UPLOAD_TTL = int(os.getenv("ANEMIA_UPLOAD_TTL_SECONDS", 60 * 60))  # segundos, por defecto 1 hora

# Evita iniciar múltiples hilos en recargas del reloader
_cleanup_started = False

def _cleanup_uploads_loop():
    import time
    while True:
        try:
            now = time.time()
            for name in os.listdir(UPLOAD_DIR):
                path = os.path.join(UPLOAD_DIR, name)
                try:
                    if not os.path.isfile(path):
                        continue
                    mtime = os.path.getmtime(path)
                    if now - mtime > UPLOAD_TTL:
                        try:
                            os.remove(path)
                        except Exception:
                            pass
                except Exception:
                    continue
        except Exception:
            pass
        # Dormir un tiempo (media del TTL o 5 minutos mínimo)
        sleep_for = max(300, UPLOAD_TTL // 2)
        time.sleep(sleep_for)

def start_upload_cleanup_daemon():
    global _cleanup_started
    if not ENABLE_UPLOAD_CLEANUP:
        return
    if _cleanup_started:
        return
    try:
        import threading
        t = threading.Thread(target=_cleanup_uploads_loop, name="anemia-upload-cleaner", daemon=True)
        t.start()
        _cleanup_started = True
    except Exception:
        pass

# Iniciar limpieza automáticamente al importar el módulo (si está habilitado)
start_upload_cleanup_daemon()

def threshold_by_age(age_months: float | int | None) -> float:
    """
    Devuelve el umbral de Hb en g/dL para decidir anemia según edad:
      6–59  meses  -> 11.0 + OFFSET_SMALL
      60–131 meses -> 11.5 + OFFSET_BIG
      otros        -> 11.5 + OFFSET_BIG (fallback)
    """
    if age_months is None:
        return 11.5 + OFFSET_BIG
    a = float(age_months)
    if 6 <= a <= 59:
        return 11.0 + OFFSET_SMALL
    elif 60 <= a <= 131:
        return 11.5 + OFFSET_BIG
    else:
        return 11.5 + OFFSET_BIG

# La carga del modelo y las funciones de inferencia/resumen están en
# `src.api.vision_anemia_core` para evitar import circular entre las tareas

# ---------- ENDPOINT PARA ROUTER ----------

@router.post("/anemia")
async def anemia_endpoint(
    file: UploadFile = File(..., description="Imagen del párpado palpebral (PNG/JPG)"),
    age_months: float = Form(..., description="Edad del infante en meses")
):
    """
    Detecta anemia en infantes mediante análisis de imagen del párpado palpebral.
    
    Parámetros:
    - file: Imagen del párpado (PNG/JPG)
    - age_months: Edad del infante en meses
    
    Retorna:
    - hb_estimate_g_dL: Hemoglobina estimada (g/dL)
    - threshold_g_dL: Umbral de Hb según edad
    - anemia_flag: True si es anémico, False si no
    - anemia_label: Etiqueta legible
    """
    try:
        # Validar tipo MIME
        if file.content_type not in ALLOWED_MIME:
            raise HTTPException(status_code=415, detail=f"Tipo de archivo no soportado: {file.content_type}")

        # Leer hasta MAX_FILE_SIZE + 1 para detectar overflow
        content = await file.read(MAX_FILE_SIZE + 1)
        if not content:
            raise HTTPException(status_code=400, detail="No se pudo leer el archivo de imagen.")
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"Archivo demasiado grande. Máximo {MAX_FILE_SIZE} bytes.")

        # Verificar que Pillow puede abrir la imagen
        try:
            pil_img = Image.open(io.BytesIO(content))
            pil_img.verify()
        except (UnidentifiedImageError, Exception):
            raise HTTPException(status_code=400, detail="El archivo subido no es una imagen válida.")

        # Guardar temporalmente (solo para registro / debugging)
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
        if ext not in ALLOWED_EXT:
            # forzar extensión accept
            ext = ".jpg"
        tmp_name = f"{uuid.uuid4().hex}{ext}"
        tmp_path = os.path.join(UPLOAD_DIR, tmp_name)
        try:
            with open(tmp_path, "wb") as f:
                f.write(content)
            # Si está en modo asíncrono, encolar tarea
            if ANEMIA_ASYNC:
                if not infer_anemia or not celery_app:
                    raise HTTPException(status_code=500, detail="Modo asíncrono no está disponible (falla import Celery).")

                task = infer_anemia.delay(tmp_path, age_months)
                return JSONResponse({"task_id": task.id, "status": "PENDING"})

            # Inferencia síncrona
            hb = predict_hb_from_bytes(content)
        finally:
            # Si estamos en modo asíncrono, dejamos el archivo para que el worker lo procese.
            if not ANEMIA_ASYNC:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass

        thr = threshold_by_age(age_months)
        anemia_flag = hb < thr

        result = {
            "age_months": age_months,
            "hb_estimate_g_dL": round(hb, 2),
            "threshold_g_dL": round(thr, 2),
            "anemia_flag": bool(anemia_flag),
            "anemia_label": "Anémico" if anemia_flag else "No anémico",
        }

        return JSONResponse(result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")


@router.get('/anemia/status/{task_id}')
def anemia_status(task_id: str):
    """Consulta el estado de una tarea en Celery (solo si ANEMIA_ASYNC está activo)."""
    if not ANEMIA_ASYNC:
        raise HTTPException(status_code=400, detail="Modo asíncrono no está activado en este servicio.")
    if not celery_app:
        raise HTTPException(status_code=500, detail="Celery no está disponible en este servicio.")

    res = celery_app.AsyncResult(task_id)
    info = {"task_id": task_id, "status": res.status}
    try:
        if res.status == 'SUCCESS':
            info['result'] = res.result
    except Exception:
        pass
    return JSONResponse(info)
