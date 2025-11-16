#!/usr/bin/env python3
"""
Script de prueba para subir una imagen al endpoint /api/vision/anemia
Uso:
    python backend/scripts/test_anemia_upload.py /ruta/a/imagen.jpg 24

Devuelve la respuesta JSON del servicio.
"""
import sys
import requests

if len(sys.argv) < 3:
    print("Uso: test_anemia_upload.py /ruta/a/imagen.jpg age_months")
    sys.exit(1)

img_path = sys.argv[1]
age = sys.argv[2]

url = "http://localhost:8000/api/vision/anemia"
with open(img_path, "rb") as f:
    files = {"file": (img_path, f, "image/jpeg")}
    data = {"age_months": age}
    r = requests.post(url, files=files, data=data, timeout=30)
    try:
        print(r.status_code)
        print(r.json())
    except Exception:
        print(r.text)
