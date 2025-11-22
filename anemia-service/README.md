# Servicio de Detección de Anemia - ONNX Model (Actualizado)

## Resumen de Cambios

Este README documenta el servicio de detección de anemia usando **ONNX Runtime** desde Hugging Face con FastAPI, sin dependencias de Celery, Redis o PyTorch.

### ✨ Mejoras Principales

- ✅ **Modelo ONNX ligero** desde Hugging Face (`mprasca/anemia_model`)
- ✅ **Descarga automática** del modelo durante el build de Docker
- ✅ **FastAPI directo** sin Celery (sin Redis)
- ✅ **Imagen base optimizada**: `python:3.11-slim` 
- ✅ **Preprocesamiento preciso** con CLAHE en espacio LAB
- ✅ **Endpoints RESTful** simples y directos
- ✅ **Health checks** integrados
- ✅ **Logging completo** para debugging

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│         Docker Compose Orquestación                  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────┐      ┌──────────────┐          │
│  │   Frontend     │      │   Backend    │          │
│  │  (Next.js)     │      │  (FastAPI)   │          │
│  │  Puerto 3000   │      │  Puerto 8000 │          │
│  └────────────────┘      └──────────────┘          │
│         │                       │                    │
│         └───────────┬───────────┘                   │
│                     │                                │
│         ┌───────────▼───────────┐                  │
│         │ Anemia Service (ONNX) │                  │
│         │  Modelo: Hugging Face │                  │
│         │   Puerto: 8001        │                  │
│         └───────────────────────┘                  │
│                     │                                │
│         ┌───────────▼───────────┐                  │
│         │  Base de Datos        │                  │
│         │  (PostgreSQL)         │                  │
│         └───────────────────────┘                  │
│                                                       │
└─────────────────────────────────────────────────────┘
```

## Especificaciones del Modelo

### Entrada (Input)
- **Formato**: Tensor ONNX
- **Shape**: `(1, 3, 256, 256)` (batch, channels, height, width)
- **Dtype**: `float32`
- **Rango**: `[0, 1]` (normalizado)

### Salida (Output)
- **Formato**: Valor único float
- **Significado**: Estimación de hemoglobina en g/dL

### Preprocesamiento Crítico (¡EXACTAMENTE como se especifica!)

1. **Convertir a LAB**: RGB → LAB
2. **CLAHE en canal L**: `clipLimit=2.0, tileGridSize=(8,8)`
3. **Convertir a RGB**: LAB → RGB
4. **Redimensionar**: Mantener aspect ratio, lado más grande = 256px
5. **Centrar**: Canvas 256×256 con padding reflejado (`cv2.BORDER_REFLECT`)
6. **Normalizar**: Dividir por 255.0 → rango [0, 1]
7. **HWC→CHW**: (H, W, 3) → (3, H, W)
8. **Agregar batch**: (3, 256, 256) → (1, 3, 256, 256)

## Despliegue

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar o actualizar el repositorio
git clone <repo> && cd evaluacion-nutricional-publico

# Desplegar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs del servicio de anemia
docker-compose logs -f anemia-service
```

**Servicios disponibles:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- **Anemia Service: http://localhost:8001**
- Base de datos: localhost:5432

### Opción 2: Ejecutar solo el servicio de anemia

```bash
# Desde el directorio raíz del proyecto
docker build -f Dockerfile.anemia -t anemia-service:latest .

# Ejecutar contenedor
docker run -d \
  -p 8001:8000 \
  -v anemia_models:/app/models \
  --name anemia-service \
  anemia-service:latest

# Ver logs
docker logs -f anemia-service
```

### Opción 3: Ejecución local (desarrollo)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r anemia-service/requirements.txt

# 3. Ejecutar
cd anemia-service
python main.py

# O con uvicorn explícitamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Predicción de Anemia
```bash
POST /predict
```

**Request (multipart/form-data):**
```
file: <imagen.jpg>
age_months: 24
```

**Response:**
```json
{
  "age_months": 24.0,
  "hb_estimate_g_dL": 11.8,
  "threshold_g_dL": 12.0,
  "anemia_flag": true,
  "anemia_label": "Anémico"
}
```

### 3. Información del Servicio
```bash
GET /
```

**Response:**
```json
{
  "service": "Anemia Detection Service",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict (POST)",
    "docs": "/docs",
    "openapi": "/openapi.json"
  }
}
```

## Ejemplos de Uso

### Con cURL

```bash
# Predicción básica
curl -X POST "http://localhost:8001/predict" \
  -F "file=@/path/to/conjunctiva.jpg" \
  -F "age_months=24"

# Health check
curl http://localhost:8001/health

# Documentación interactiva
curl http://localhost:8001/docs
```

### Con Python

```python
import requests
import json

ANEMIA_SERVICE_URL = "http://localhost:8001"

# Preparar imagen
with open("conjunctiva.jpg", "rb") as f:
    files = {"file": f}
    data = {"age_months": 24}
    
    # Predicción
    response = requests.post(
        f"{ANEMIA_SERVICE_URL}/predict",
        files=files,
        data=data
    )
    
    print(json.dumps(response.json(), indent=2))
```

### Con JavaScript/TypeScript

```typescript
const anemia_service_url = "http://localhost:8001";

async function predictAnemia(imageFile: File, ageMonths: number) {
  const formData = new FormData();
  formData.append("file", imageFile);
  formData.append("age_months", ageMonths.toString());
  
  const response = await fetch(`${anemia_service_url}/predict`, {
    method: "POST",
    body: formData
  });
  
  return await response.json();
}

// Uso
const input = document.getElementById("imageInput") as HTMLInputElement;
const file = input.files?.[0];
if (file) {
  const result = await predictAnemia(file, 24);
  console.log(result);
}
```

## Integración con Backend Principal

El backend principal hace proxy automático al servicio de anemia a través del endpoint:

```
POST /api/vision/anemia
```

Las solicitudes se reenvían directamente al servicio en `http://anemia-service:8000/predict`.

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/vision/anemia" \
  -F "file=@image.jpg" \
  -F "age_months=24"
```

## Umbrales Clínicos (OMS)

| Rango de Edad | Umbral (g/dL) | Clasificación            |
|---------------|----|--------------------------|
| 6-59 meses    | 12.0  | Anémico si Hb < umbral   |
| 60-131 meses  | 12.25 | Anémico si Hb < umbral   |

El servicio calcula automáticamente el umbral según la edad proporcionada.

## Dependencias Python

```
fastapi==0.115.5
uvicorn[standard]==0.32.1
numpy==2.1.3
onnxruntime==1.20.1
opencv-python-headless==4.10.0.84
pillow==11.0.0
python-multipart==0.0.20
huggingface-hub==0.26.5
```

### ✅ NO incluye:
- PyTorch (solo ONNX Runtime)
- Celery (procesamiento sincrónico)
- Redis (no necesario)
- Google Drive API (modelo en Hugging Face)

## Variables de Entorno

```bash
# Configuración del servicio de anemia (en docker-compose.yml)
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

## Logs y Debugging

### Ver logs en tiempo real
```bash
# Docker Compose
docker-compose logs -f anemia-service

# Docker directo
docker logs -f anemia_service
```

### Debugging local
```bash
# Con logging verbose
PYTHONUNBUFFERED=1 python -u main.py
```

Los logs muestran:
- 📥 Descarga del modelo desde Hugging Face
- ✅ Inicialización de ONNX Runtime
- 🔄 Preprocesamiento de imagen
- 🧠 Ejecución del modelo
- 📊 Resultados de la predicción

## Solución de Problemas

### Problema: "Model not found"
```
❌ Error descargando modelo: ...
```

**Solución**: 
- Verificar conexión a internet
- El modelo se descargará automáticamente en el build
- Revisar permisos de escritura en `/app/models`

### Problema: "Service not healthy"
```
⚠️ Servicio de anemia no disponible
```

**Solución**:
```bash
# Verificar que el contenedor está corriendo
docker ps | grep anemia

# Revisar logs
docker-compose logs anemia-service

# Recrear el contenedor
docker-compose down anemia-service
docker-compose up anemia-service
```

### Problema: Timeout en predicción
```
❌ Timeout al conectar con servicio de anemia
```

**Solución**:
- Aumentar timeout en backend: `timeout=30.0` en `vision_anemia_onnx.py`
- Verificar recursos disponibles (RAM, CPU)
- Ver logs: `docker-compose logs anemia-service`

### Problema: Imagen no válida
```
❌ El archivo subido no es una imagen válida
```

**Solución**:
- Verificar formato: PNG o JPG
- Verificar que no esté corrupta
- Tamaño máximo: 5 MB (configurable)

## Archivos Modificados/Eliminados

### Nuevos:
- ✨ `anemia-service/main.py` - Servicio FastAPI con ONNX
- ✨ `anemia-service/requirements.txt` - Dependencias optimizadas
- ✨ `Dockerfile.anemia` - Dockerfile optimizado para python:3.11-slim

### Modificados:
- 🔄 `docker-compose.yml` - Añadido servicio anemia, eliminados Redis y Celery
- 🔄 `backend/src/api/vision_anemia_onnx.py` - Proxy HTTP en lugar de Celery

### Eliminados:
- ❌ Referencias a `REDIS_URL` del backend
- ❌ Configuración de `ANEMIA_ASYNC` (siempre síncrono ahora)
- ❌ Tareas de Celery (`src/tasks/celery_app.py`, `src/tasks/anemia_tasks.py`)
- ❌ Dependencias PyTorch
- ❌ Descargas desde Google Drive

## Rendimiento

- **Tiempo de inicio**: ~10-15 segundos (descarga del modelo en primer build)
- **Tiempo de predicción**: 100-300ms (según CPU)
- **Uso de memoria**: ~500 MB RAM
- **Tamaño de imagen Docker**: ~1.2 GB

## Monitoreo y Observabilidad

### Health Check automático
```bash
docker-compose ps anemia-service
# HEALTHCHECK: Hace ping cada 30 segundos
```

### Métricas disponibles
- Logs estructurados en JSON (opcionalmente)
- Endpoint `/docs` con Swagger UI
- OpenAPI spec en `/openapi.json`

## Migrando desde la versión anterior

Si tenías la versión antigua con Celery:

```bash
# 1. Parar los servicios
docker-compose down

# 2. Actualizar código
git pull

# 3. Reconstruir imágenes
docker-compose build --no-cache

# 4. Iniciar servicios
docker-compose up -d

# 5. Verificar
docker-compose ps
curl http://localhost:8001/health
```

## Próximos Pasos Recomendados

- [ ] Integrar autenticación al endpoint
- [ ] Agregar rate limiting
- [ ] Implementar caching de modelos
- [ ] Agregar métricas con Prometheus
- [ ] Configurar Kubernetes deployment
- [ ] Tests unitarios del preprocesamiento

## Referencia

- **Modelo**: [mprasca/anemia_model en Hugging Face](https://huggingface.co/mprasca/anemia_model)
- **Framework**: FastAPI, ONNX Runtime, OpenCV, NumPy
- **Python**: 3.11+
- **Licencia**: [Ver LICENSE](../LICENSE)

---

**Última actualización**: Noviembre 2025
