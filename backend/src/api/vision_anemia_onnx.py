# vision_anemia_onnx.py
# Módulo para hacer proxy a detección de anemia usando el servicio ONNX remoto

import io
import os
import logging
from typing import Optional
import httpx

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Crear router para integrarse con el backend principal
router = APIRouter()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URL del servicio de anemia (por defecto en Docker Compose)
ANEMIA_SERVICE_URL = os.getenv("ANEMIA_SERVICE_URL", "http://anemia-service:8000")

# Validación de uploads
MAX_FILE_SIZE = int(os.getenv("ANEMIA_MAX_FILE_SIZE", 5 * 1024 * 1024))  # 5 MB por defecto
ALLOWED_MIME = {"image/jpeg", "image/png"}
ALLOWED_EXT = {".jpg", ".jpeg", ".png"}

logger.info(f"✅ Anemia Service usando: {ANEMIA_SERVICE_URL}")


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

async def verify_anemia_service_health():
    """Verifica que el servicio de anemia esté disponible"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ANEMIA_SERVICE_URL}/health", timeout=5.0)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Error al verificar salud del servicio de anemia: {str(e)}")
        return False


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/anemia")
async def anemia_endpoint(
    file: UploadFile = File(..., description="Imagen del párpado palpebral (PNG/JPG)"),
    age_months: float = Form(..., description="Edad del infante en meses")
):
    """
    Detecta anemia en infantes mediante análisis de imagen del párpado palpebral.
    
    Hace proxy a través del servicio de anemia dedicado que ejecuta el modelo ONNX.
    
    Parámetros:
    - file: Imagen del párpado (PNG/JPG)
    - age_months: Edad del infante en meses
    
    Retorna:
    {
        "age_months": float,
        "hb_estimate_g_dL": float,
        "threshold_g_dL": float,
        "anemia_flag": bool,
        "anemia_label": string
    }
    """
    try:
        # Validar tipo MIME
        if file.content_type not in ALLOWED_MIME:
            raise HTTPException(
                status_code=415,
                detail=f"Tipo de archivo no soportado: {file.content_type}. "
                        f"Usar: {', '.join(ALLOWED_MIME)}"
            )

        # Leer hasta MAX_FILE_SIZE + 1 para detectar overflow
        content = await file.read(MAX_FILE_SIZE + 1)
        if not content:
            raise HTTPException(status_code=400, detail="No se pudo leer el archivo de imagen.")
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo {MAX_FILE_SIZE / 1024 / 1024:.1f} MB."
            )

        # Verificar que es una imagen válida
        try:
            pil_img = Image.open(io.BytesIO(content))
            pil_img.verify()
        except (UnidentifiedImageError, Exception) as e:
            logger.warning(f"⚠️  Imagen inválida: {str(e)}")
            raise HTTPException(status_code=400, detail="El archivo subido no es una imagen válida.")

        # Validar edad
        if age_months < 0:
            raise HTTPException(status_code=400, detail="age_months debe ser positivo.")

        # Hacer llamada al servicio de anemia
        logger.info(f"📤 Enviando solicitud a {ANEMIA_SERVICE_URL}/predict | Edad: {age_months} meses")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ANEMIA_SERVICE_URL}/predict",
                    files={"file": (file.filename, content, file.content_type)},
                    data={"age_months": age_months}
                )
                
                if response.status_code != 200:
                    error_msg = f"Servicio de anemia retornó {response.status_code}"
                    try:
                        error_detail = response.json()
                        logger.error(f"❌ {error_msg}: {error_detail}")
                    except:
                        logger.error(f"❌ {error_msg}: {response.text}")
                    
                    raise HTTPException(
                        status_code=500,
                        detail="Error al procesar la imagen en el servicio de anemia"
                    )
                
                result = response.json()
                logger.info(f"✅ Predicción exitosa: {result}")
                return JSONResponse(result)
                
        except httpx.ConnectError as e:
            logger.error(f"❌ No se puede conectar al servicio de anemia en {ANEMIA_SERVICE_URL}: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Servicio de anemia no disponible. Intente más tarde."
            )
        except httpx.TimeoutException:
            logger.error(f"❌ Timeout al conectar con servicio de anemia")
            raise HTTPException(
                status_code=504,
                detail="Timeout al procesar la solicitud en el servicio de anemia"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error no esperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")


@router.get("/anemia/health")
async def anemia_health():
    """
    Verifica la salud del servicio de anemia
    """
    try:
        is_healthy = await verify_anemia_service_health()
        if is_healthy:
            return {"status": "healthy", "service": "anemia_model"}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "service": "anemia_model", "reason": "Service not responding"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "service": "anemia_model", "reason": str(e)}
        )

