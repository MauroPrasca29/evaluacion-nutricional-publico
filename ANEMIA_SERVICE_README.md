# Servicio de Detección de Anemia - Vision ONNX

Este servicio implementa un modelo de visión computacional para la detección de anemia en infantes mediante análisis del párpado palpebral, utilizando **ONNX Runtime** para inferencia eficiente.

## Archivos del Proyecto

- **`backend/models/hb_regressor_infants_ft.onnx`** - Modelo ONNX preentrenado (107 MB)
- **`backend/models/hb_regressor_infants_ft.pth`** - Modelo PyTorch original (107 MB)
- **`backend/src/api/vision_anemia_onnx.py`** - Servicio FastAPI
- **`Dockerfile.anemia`** - Container para el servicio
- **`backend/requirements.txt`** - Dependencias Python actualizadas

## Características

✅ Detección de anemia basada en análisis de imágenes  
✅ Umbrales ajustados por grupo de edad  
✅ API REST con FastAPI  
✅ Inferencia eficiente con ONNX Runtime  
✅ Preprocesamiento de imágenes con CLAHE  
✅ Containerizado con Docker  

## Dependencias

Las siguientes dependencias se han agregado a `requirements.txt`:

```
onnxruntime==1.19.2
opencv-python-headless==4.10.0.84
numpy==1.26.4
pillow==10.4.0
```

## Umbrales de Hemoglobina (Hb) por Edad

El servicio utiliza los siguientes umbrales para clasificar anemia:

| Rango de Edad | Umbral Hb (g/dL) |
|---------------|------------------|
| 6-59 meses    | 12.0 (11.0 + 1.00) |
| 60-131 meses  | 12.25 (11.5 + 0.75) |

- **Si Hb < umbral**: Anémico ❌
- **Si Hb ≥ umbral**: No anémico ✅

## API Endpoint

### POST `/api/vision/anemia`

**Parámetros:**
- `file` (form-data, requerido): Imagen del párpado palpebral (PNG/JPG)
- `age_months` (form-data, requerido): Edad del infante en meses (float)

**Response:**
```json
{
  "age_months": 24.5,
  "hb_estimate_g_dL": 11.8,
  "threshold_g_dL": 12.0,
  "anemia_flag": true,
  "anemia_label": "Anémico"
}
```

## Uso Local

### Opción 1: Ejecutar con Docker Compose

```bash
# Iniciar el servicio
docker-compose up anemia-service

# El servicio estará disponible en http://localhost:8001
```

### Opción 2: Ejecutar directamente

```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar el servicio
cd /app
uvicorn vision_anemia_onnx:app --host 0.0.0.0 --port 8000
```

## Pruebas

### Con cURL

```bash
curl -X POST "http://localhost:8001/api/vision/anemia" \
  -F "file=@/path/to/image.jpg" \
  -F "age_months=24"
```

### Con Python

```python
import requests

with open("image.jpg", "rb") as f:
    files = {"file": f}
    data = {"age_months": 24}
    response = requests.post("http://localhost:8001/api/vision/anemia", files=files, data=data)
    print(response.json())
```

## Estructura de Preprocesamiento

1. **Lectura de imagen**: Convierte a RGB usando Pillow
2. **CLAHE**: Applica Contrast Limited Adaptive Histogram Equalization en canal L (LAB)
3. **Redimensionamiento**: Escala manteniendo proporción
4. **Padding**: Refleja bordes para llegar a 256x256
5. **Normalización**: Convierte a float32 [0,1]
6. **Transposición**: Convierte de HWC a CHW para ONNX

## Variables de Entorno

- `ANEMIA_ONNX_PATH`: Ruta del modelo ONNX (default: `models/hb_regressor_infants_ft.onnx`)
 - `ANEMIA_ASYNC`: `true|false` — habilita el flujo asíncrono con Celery+Redis (default: `false`)
 - `ANEMIA_ENABLE_UPLOAD_CLEANUP`: `true|false` — habilita limpieza automática de uploads (default: `true`)
 - `ANEMIA_UPLOAD_TTL_SECONDS`: segundos antes de borrar un upload (default: `3600`)
 - `ANEMIA_UPLOAD_DIR`: ruta donde almacenar uploads (default: `/tmp/uploads`)

## Estructura de Carpetas

```
/app/
├── models/
│   └── hb_regressor_infants_ft.onnx
├── vision_anemia_onnx.py
└── requirements.txt
```

## Notas Técnicas

- El modelo espera imágenes en formato **NCHW** (1, 3, 256, 256)
- La inferencia se realiza en **CPU** (configurable en código)
- El servicio es **stateless** y puede escalarse horizontalmente
- Todas las imágenes se procesan en memoria (sin almacenamiento temporal)

## Próximos Pasos

- [ ] Integrar con el endpoint principal del backend
- [ ] Agregar autenticación y rate limiting
- [ ] Implementar logging avanzado con Sentry
- [ ] Agregar cache de resultados con Redis
- [ ] Crear tests unitarios e integración
 
## Flujo Asíncrono (Celery + Redis)

1. Levanta servicios con `docker-compose up -d redis celery_worker backend` (ya incluido en `docker-compose.yml`).
2. Envío de tarea: `POST /api/vision/anemia` devuelve `{ "task_id": "...", "status":"PENDING" }`.
3. Consultar estado: `GET /api/vision/anemia/status/{task_id}` — devuelve `PENDING`/`SUCCESS`/`FAILURE`. Si `SUCCESS`, incluye el resultado.

La carpeta `./backend/uploads` se monta en `/tmp/uploads` dentro de los contenedores y se usa como zona temporal compartida entre backend y worker. Los uploads se borran automáticamente según `ANEMIA_UPLOAD_TTL_SECONDS` si `ANEMIA_ENABLE_UPLOAD_CLEANUP=true`.
