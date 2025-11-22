"""
Servicio de Detección de Anemia - Vision ONNX
Detecta anemia en infantes mediante análisis de imágenes de conjuntiva ocular
Utiliza modelo ONNX de Hugging Face: mprasca/anemia_model
"""

import io
import logging
from typing import Optional
from contextlib import asynccontextmanager

import numpy as np
import onnxruntime as rt
import cv2
from PIL import Image
from fastapi import FastAPI, File, Form, HTTPException
from fastapi.responses import JSONResponse
from huggingface_hub import snapshot_download
import os

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================
MODEL_PATH = None
SESSION = None
MODEL_HF_REPO = "mprasca/anemia_model"
MODELS_DIR = "/app/models"

# ============================================================================
# FUNCIONES DE INICIALIZACIÓN
# ============================================================================

def download_model():
    """
    Descarga el modelo ONNX desde Hugging Face si no existe localmente
    """
    global MODEL_PATH
    
    try:
        logger.info(f"📥 Descargando modelo de {MODEL_HF_REPO}...")
        model_dir = snapshot_download(
            repo_id=MODEL_HF_REPO,
            repo_type="model",
            cache_dir=MODELS_DIR,
            local_dir=f"{MODELS_DIR}/anemia_model"
        )
        
        # El archivo se llama hb_regressor_infants_ft.onnx en Hugging Face
        MODEL_PATH = os.path.join(model_dir, "hb_regressor_infants_ft.onnx")
        
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        
        logger.info(f"✅ Modelo descargado exitosamente: {MODEL_PATH}")
        return MODEL_PATH
    except Exception as e:
        logger.error(f"❌ Error descargando modelo: {str(e)}")
        raise


def initialize_model():
    """
    Inicializa la sesión ONNX Runtime
    """
    global SESSION, MODEL_PATH
    
    try:
        if MODEL_PATH is None:
            MODEL_PATH = download_model()
        
        # Crear directorio de modelos si no existe
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        logger.info(f"🔧 Inicializando ONNX Runtime con modelo: {MODEL_PATH}")
        SESSION = rt.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
        logger.info("✅ ONNX Runtime inicializado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando ONNX Runtime: {str(e)}")
        raise


# ============================================================================
# FUNCIONES DE PREPROCESAMIENTO DE IMAGEN
# ============================================================================

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocesa la imagen siguiendo exactamente el protocolo especificado:
    
    1. Convertir de RGB a espacio de color LAB
    2. Aplicar CLAHE solo al canal L (clipLimit=2.0, tileGridSize=(8,8))
    3. Convertir de vuelta a RGB
    4. Redimensionar manteniendo aspect ratio (lado más grande = 256px)
    5. Centrar en canvas 256x256 con padding reflejado (cv2.BORDER_REFLECT)
    6. Normalizar a rango [0, 1] dividiendo por 255.0
    7. Convertir HWC a CHW
    8. Agregar dimensión de batch: (1, 3, 256, 256)
    """
    try:
        # Cargar imagen desde bytes
        image_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_array = np.array(image_pil)  # Shape: (H, W, 3), dtype: uint8
        
        logger.debug(f"📸 Imagen cargada: {image_array.shape}, dtype: {image_array.dtype}")
        
        # Paso 1: Convertir RGB a LAB
        image_lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        logger.debug(f"✅ Convertido a LAB: {image_lab.shape}")
        
        # Paso 2: Aplicar CLAHE solo al canal L
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image_lab[:, :, 0] = clahe.apply(image_lab[:, :, 0])
        logger.debug("✅ CLAHE aplicado al canal L")
        
        # Paso 3: Convertir de vuelta a RGB
        image_rgb = cv2.cvtColor(image_lab, cv2.COLOR_LAB2RGB)
        logger.debug("✅ Convertido de vuelta a RGB")
        
        # Paso 4: Redimensionar manteniendo aspect ratio
        h, w = image_rgb.shape[:2]
        max_dim = max(h, w)
        scale = 256.0 / max_dim
        new_h = int(h * scale)
        new_w = int(w * scale)
        image_resized = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        logger.debug(f"✅ Redimensionado a: {image_resized.shape}")
        
        # Paso 5: Centrar en canvas 256x256 con padding reflejado
        target_size = 256
        delta_h = target_size - new_h
        delta_w = target_size - new_w
        top = delta_h // 2
        left = delta_w // 2
        bottom = delta_h - top
        right = delta_w - left
        
        image_padded = cv2.copyMakeBorder(
            image_resized,
            top, bottom, left, right,
            cv2.BORDER_REFLECT
        )
        logger.debug(f"✅ Imagen centrada y padded: {image_padded.shape}")
        
        # Paso 6: Normalizar a rango [0, 1]
        image_normalized = image_padded.astype(np.float32) / 255.0
        logger.debug(f"✅ Normalizado: min={image_normalized.min()}, max={image_normalized.max()}")
        
        # Paso 7: Convertir HWC a CHW
        image_chw = np.transpose(image_normalized, (2, 0, 1))
        logger.debug(f"✅ Convertido a CHW: {image_chw.shape}")
        
        # Paso 8: Agregar dimensión de batch
        image_batch = np.expand_dims(image_chw, 0)
        logger.debug(f"✅ Dimensión de batch agregada: {image_batch.shape}")
        
        assert image_batch.shape == (1, 3, 256, 256), f"Forma incorrecta: {image_batch.shape}"
        assert image_batch.dtype == np.float32, f"Dtype incorrecto: {image_batch.dtype}"
        
        return image_batch
        
    except Exception as e:
        logger.error(f"❌ Error en preprocesamiento de imagen: {str(e)}")
        raise


# ============================================================================
# FUNCIONES DE LÓGICA CLÍNICA
# ============================================================================

def get_threshold_and_label(age_months: float, hb_estimate: float) -> tuple:
    """
    Calcula el umbral de hemoglobina según la edad (OMS)
    y determina si hay anemia
    
    Returns: (threshold_g_dL, anemia_flag, anemia_label)
    """
    if 6 <= age_months <= 59:
        threshold = 12.0
    elif 60 <= age_months <= 131:
        threshold = 12.25
    else:
        logger.warning(f"⚠️ Edad {age_months} meses fuera de rango definido")
        threshold = 12.0  # Default
    
    anemia_flag = hb_estimate < threshold
    anemia_label = "Anémico" if anemia_flag else "No anémico"
    
    logger.info(f"🏥 Edad: {age_months} meses, Umbral: {threshold} g/dL, "
                f"Hb: {hb_estimate:.2f} g/dL → {anemia_label}")
    
    return threshold, anemia_flag, anemia_label


# ============================================================================
# FUNCIONES DE INFERENCIA
# ============================================================================

def predict_hb(image_input: np.ndarray) -> float:
    """
    Ejecuta el modelo ONNX para predecir hemoglobina
    """
    global SESSION
    
    if SESSION is None:
        raise RuntimeError("Modelo no inicializado")
    
    try:
        # Obtener nombres de entrada y salida
        input_name = SESSION.get_inputs()[0].name
        output_name = SESSION.get_outputs()[0].name
        
        logger.debug(f"📊 Input: {input_name}, Output: {output_name}")
        
        # Ejecutar inferencia
        result = SESSION.run([output_name], {input_name: image_input})
        hb_estimate = float(result[0][0])
        
        logger.info(f"✅ Predicción: Hb = {hb_estimate:.2f} g/dL")
        
        return hb_estimate
        
    except Exception as e:
        logger.error(f"❌ Error en inferencia: {str(e)}")
        raise


# ============================================================================
# LIFESPAN - INICIALIZACIÓN Y LIMPIEZA
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de vida de la aplicación
    startup: Inicializa el modelo
    shutdown: Limpieza
    """
    logger.info("🚀 Iniciando aplicación...")
    try:
        initialize_model()
        logger.info("✅ Aplicación lista para recibir solicitudes")
    except Exception as e:
        logger.error(f"❌ Error al iniciar: {str(e)}")
        raise
    
    yield
    
    logger.info("🛑 Cerrando aplicación...")
    # Limpieza si es necesaria


# ============================================================================
# CREACIÓN DE LA APLICACIÓN FASTAPI
# ============================================================================

app = FastAPI(
    title="Anemia Detection Service",
    description="Detección de anemia en infantes mediante análisis de imágenes",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud
    """
    try:
        if SESSION is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "reason": "Model not initialized"}
            )
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"❌ Health check error: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": str(e)}
        )


@app.post("/predict")
async def predict(
    file: bytes = File(...),
    age_months: float = Form(...)
):
    """
    Endpoint principal de predicción de anemia
    
    Parámetros:
    - file: Imagen de conjuntiva ocular (multipart/form-data)
    - age_months: Edad del infante en meses
    
    Respuesta:
    {
        "age_months": float,
        "hb_estimate_g_dL": float,
        "threshold_g_dL": float,
        "anemia_flag": bool,
        "anemia_label": string
    }
    """
    try:
        logger.info(f"📥 Nueva solicitud de predicción | Edad: {age_months} meses")
        
        # Validar edad
        if age_months < 0:
            raise ValueError("age_months debe ser positivo")
        
        # Validar que el archivo no esté vacío
        if not file or len(file) == 0:
            raise ValueError("Archivo de imagen vacío")
        
        # Preprocesar imagen
        logger.info("🔄 Preprocesando imagen...")
        image_input = preprocess_image(file)
        
        # Realizar predicción
        logger.info("🧠 Ejecutando modelo...")
        hb_estimate = predict_hb(image_input)
        
        # Lógica clínica
        threshold, anemia_flag, anemia_label = get_threshold_and_label(age_months, hb_estimate)
        
        response = {
            "age_months": age_months,
            "hb_estimate_g_dL": round(hb_estimate, 2),
            "threshold_g_dL": threshold,
            "anemia_flag": bool(anemia_flag),
            "anemia_label": anemia_label
        }
        
        logger.info(f"✅ Respuesta: {response}")
        return response
        
    except ValueError as e:
        logger.error(f"⚠️ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """
    Endpoint raíz con información del servicio
    """
    return {
        "service": "Anemia Detection Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
