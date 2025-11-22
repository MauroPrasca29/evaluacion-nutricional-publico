"""
Endpoint para detección de anemia usando el modelo ONNX
Conecta con el servicio de anemia en puerto 8001
"""

import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# URL del servicio de anemia
ANEMIA_SERVICE_URL = "http://anemia-service:8000"


@router.post("/predict-anemia")
async def predict_anemia(
    file: UploadFile = File(...),
    age_months: float = Form(...)
):
    """
    Predice anemia basada en imagen de ojo y edad del infante
    
    Parámetros:
    - file: Imagen de la conjuntiva ocular (JPG/PNG)
    - age_months: Edad en meses
    
    Respuesta:
    {
        "age_months": float,
        "hb_estimate_g_dL": float,
        "threshold_g_dL": float,
        "anemia_flag": bool,
        "anemia_label": string,
        "recommendation": string
    }
    """
    try:
        # Leer contenido del archivo
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        
        # Hacer llamada al servicio de anemia
        logger.info(f"Prediciendo anemia - Edad: {age_months} meses")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ANEMIA_SERVICE_URL}/predict",
                files={"file": (file.filename, content, file.content_type)},
                data={"age_months": age_months}
            )
            
            if response.status_code != 200:
                logger.error(f"Error en servicio de anemia: {response.status_code}")
                raise HTTPException(
                    status_code=500,
                    detail="Error al procesar imagen en servicio de anemia"
                )
            
            result = response.json()
            
            # Agregar recomendación
            if result["anemia_flag"]:
                result["recommendation"] = "Se recomienda realizar un examen de sangre para confirmar anemia"
            else:
                result["recommendation"] = "Hemoglobina normal según estimación por imagen"
            
            logger.info(f"Predicción completada: {result['anemia_label']}")
            return JSONResponse(result)
            
    except httpx.ConnectError:
        logger.error(f"No se puede conectar a servicio de anemia en {ANEMIA_SERVICE_URL}")
        raise HTTPException(
            status_code=503,
            detail="Servicio de detección de anemia no disponible"
        )
    except httpx.TimeoutException:
        logger.error("Timeout en servicio de anemia")
        raise HTTPException(
            status_code=504,
            detail="Timeout al procesar imagen"
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
