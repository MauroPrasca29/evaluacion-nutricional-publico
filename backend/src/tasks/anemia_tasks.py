import os
from pathlib import Path
from src.api.vision_anemia_onnx import predict_hb_from_bytes, threshold_by_age
from tasks.celery_app import celery

@celery.task(bind=True)
def infer_anemia(self, file_path: str, age_months: float):
    """Tarea que lee un archivo en disco, ejecuta la inferencia y devuelve el resultado JSON."""
    try:
        p = Path(file_path)
        if not p.exists():
            return {"error": "file_not_found", "path": file_path}

        content = p.read_bytes()
        hb = predict_hb_from_bytes(content)
        thr = threshold_by_age(age_months)
        anemia_flag = hb < thr

        result = {
            "age_months": age_months,
            "hb_estimate_g_dL": round(hb, 2),
            "threshold_g_dL": round(thr, 2),
            "anemia_flag": bool(anemia_flag),
            "anemia_label": "Anémico" if anemia_flag else "No anémico",
        }

        return result
    except Exception as e:
        return {"error": "internal_error", "detail": str(e)}
