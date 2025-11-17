import os
import io
import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image

# Rutas posibles
POSSIBLE_PATHS = [
    "models/hb_regressor_infants_ft.onnx",
    "/app/models/hb_regressor_infants_ft.onnx",
    "./models/hb_regressor_infants_ft.onnx",
]

MODEL_PATH = os.getenv("ANEMIA_ONNX_PATH", None)
if not MODEL_PATH:
    for p in POSSIBLE_PATHS:
        if os.path.exists(p):
            MODEL_PATH = p
            break

# Cargar sesión ONNX solo si el modelo existe
session = None
input_name = None
output_name = None

if MODEL_PATH:
    try:
        session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        print(f"✅ Modelo ONNX cargado: {MODEL_PATH}")
    except Exception as e:
        print(f"⚠️  Error cargando modelo ONNX: {e}")
        session = None
else:
    print(f"⚠️  Modelo ONNX no disponible. Los endpoints de anemia no funcionarán.")

# Umbrales
OFFSET_SMALL = 1.00
OFFSET_BIG = 0.75

def threshold_by_age(age_months: float | int | None) -> float:
    if age_months is None:
        return 11.5 + OFFSET_BIG
    a = float(age_months)
    if 6 <= a <= 59:
        return 11.0 + OFFSET_SMALL
    elif 60 <= a <= 131:
        return 11.5 + OFFSET_BIG
    else:
        return 11.5 + OFFSET_BIG

def preprocess_256(img_rgb: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(2.0, (8, 8)).apply(l)
    img_lab = cv2.merge((l, a, b))
    img_rgb = cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB)

    h, w = img_rgb.shape[:2]
    s = 256 / max(h, w)
    nh, nw = int(h * s), int(w * s)
    img_resized = cv2.resize(img_rgb, (nw, nh), interpolation=cv2.INTER_AREA)

    top = (256 - nh) // 2
    bottom = 256 - nh - top
    left = (256 - nw) // 2
    right = 256 - nw - left

    img_padded = cv2.copyMakeBorder(
        img_resized, top, bottom, left, right,
        borderType=cv2.BORDER_REFLECT_101
    )

    img_float = img_padded.astype(np.float32) / 255.0
    return img_float


def predict_hb_from_bytes(img_bytes: bytes) -> float:
    if session is None:
        raise RuntimeError("Modelo ONNX no disponible. No se puede realizar la predicción.")
    
    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_rgb = np.array(pil_img)
    img = preprocess_256(img_rgb)
    img_chw = np.transpose(img, (2, 0, 1))
    img_chw = np.expand_dims(img_chw, axis=0)
    hb_pred = session.run([output_name], {input_name: img_chw})[0]
    hb_value = float(hb_pred[0][0])
    return hb_value
