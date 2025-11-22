# Integración de Detección de Anemia por Imagen

## Descripción

Se ha integrado un modelo ONNX de aprendizaje automático para detectar anemia en infantes mediante análisis de fotografías de los ojos (conjuntiva ocular). 

### Características

✅ **Análisis automático de imagen**: Sube una foto de los ojos y obtén una estimación de hemoglobina  
✅ **Prioridad de datos**: Si tienes hemoglobina por examen de sangre, se usa ese valor (mayor precisión)  
✅ **Recomendaciones clínicas**: Sugerencias automáticas basadas en el resultado  
✅ **Tab dedicado**: Nueva sección "Estado Anémico" en los resultados  

## Flujo de Uso

### 1. Crear un Nuevo Seguimiento

1. Selecciona un infante de la lista
2. Completa los datos antropométricos
3. Ve a la sección **"Exámenes Complementarios"**

### 2. Opción A: Con Hemoglobina (Examen de Sangre)

- Si tienes el resultado de un examen de sangre, ingresa el valor de hemoglobina en g/dL
- El sistema usará este valor como la fuente primaria
- **Este valor tendrá prioridad sobre la estimación por imagen**

### 3. Opción B: Sin Hemoglobina (Análisis de Imagen)

- Ve a la sección **"Fotografía Clínica para Análisis de Anemia"**
- Sube una foto clara de la **conjuntiva (parte blanca) de los ojos**
- El sistema analizará automáticamente la imagen
- Verás el resultado en tiempo real con:
  - Hemoglobina estimada (g/dL)
  - Umbral OMS según edad
  - Clasificación: **Anémico** o **Normal**
  - Recomendaciones de acción

### 4. Envío del Seguimiento

- Haz clic en **"Finalizar Seguimiento"**
- Los datos se guardan con toda la información de anemia
- Accede a los resultados en la nueva tab **"Estado Anémico"**

## Lógica de Prioridad

```
IF hemoglobina_disponible:
    usar hemoglobina (examen de sangre)
ELIF imagen_disponible:
    usar modelo ONNX (análisis de fotografía)
ELSE:
    sin determinación de anemia
```

## Recomendaciones Automáticas

### Si es Anémico:
- ⚠️ Se recomienda realizar **examen de sangre** para confirmar
- 📋 Sugerencias de alimentos ricos en hierro:
  - Carnes rojas magras
  - Hígado y vísceras
  - Huevos
  - Legumbres
  - Frutas cítricas (para absorción de hierro)

### Si es Normal:
- ✅ Hemoglobina dentro de los valores normales
- 💪 Mantener buena alimentación

## Umbrales OMS Utilizados

| Grupo de Edad | Umbral Hemoglobina |
|---|---|
| 6-59 meses | 12.0 g/dL |
| 60-131 meses | 12.25 g/dL |

## Especificaciones Técnicas

### Modelo ONNX
- **Nombre**: `hb_regressor_infants_ft.onnx`
- **Fuente**: Hugging Face (`mprasca/anemia_model`)
- **Entrada**: Imagen 256x256 RGB normalizada
- **Salida**: Estimación de hemoglobina en g/dL

### Servicio
- **URL**: `http://anemia-service:8001` (host) o `http://anemia-service:8000` (Docker)
- **Endpoint**: POST `/predict`
- **Parámetros**: 
  - `file`: Imagen (JPG/PNG)
  - `age_months`: Edad en meses (float)

### Backend
- **Endpoint**: POST `/api/vision/predict-anemia`
- **Manejo**: Proxy desde FastAPI backend al servicio ONNX
- **Timeout**: 30 segundos

## Instalación y Despliegue

### Prerequisitos
- Docker y Docker Compose
- Los servicios deben estar corriendo:
  - Frontend (port 3000)
  - Backend (port 8000)
  - Anemia Service (port 8001)
  - Database (port 5432)

### Inicio de Servicios

```bash
# En la raíz del proyecto
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs del servicio de anemia
docker-compose logs -f anemia-service
```

### Verificar Conectividad

```bash
# Desde el host
curl -F "file=@ruta/a/imagen.jpg" \
     -F "age_months=24" \
     http://localhost:8001/predict

# Desde el backend (dentro de Docker)
curl -F "file=@imagen.jpg" \
     -F "age_months=24" \
     http://anemia-service:8000/predict
```

## Estructura de Datos

### Solicitud a Modelo
```json
POST /api/vision/predict-anemia
{
  "file": "binary image data",
  "age_months": 24.5
}
```

### Respuesta del Modelo
```json
{
  "age_months": 24.5,
  "hb_estimate_g_dL": 10.12,
  "threshold_g_dL": 12.0,
  "anemia_flag": true,
  "anemia_label": "Anémico",
  "recommendation": "Se recomienda realizar un examen de sangre para confirmar anemia"
}
```

### Resultado Guardado en Sesión
```json
{
  "source": "hemoglobina" | "modelo",
  "value": 10.12,
  "threshold": 12.0,
  "isAnemic": true,
  "label": "Anémico"
}
```

## Almacenamiento en Seguimiento

El resultado de anemia se almacena en `sessionStorage` con la clave `anemia_result`:

```javascript
sessionStorage.getItem('anemia_result')
// {
//   "source": "modelo",
//   "value": 10.12,
//   "threshold": 12.0,
//   "isAnemic": true,
//   "label": "Anémico"
// }
```

## Pantallas del Flujo

### 1. Formulario - Exámenes Complementarios
- Campo de hemoglobina con etiqueta clara sobre prioridad
- Explicación: "Este valor tendrá prioridad sobre la estimación por imagen"

### 2. Formulario - Fotografía Clínica
- Carga de foto con instrucciones claras
- Indicador de carga: "Analizando imagen para detectar anemia..."
- Resultado en tiempo real con badge de color (rojo/verde)
- Muestra: Hb estimada, umbral, recomendación

### 3. Resultados - Tab "Estado Anémico"
- Tarjetas con: Fuente, Hemoglobina, Umbral OMS
- Resultado principal con icono y colores
- Recomendaciones detalladas
- Nota sobre fiabilidad de estimaciones por imagen
- Parámetros técnicos de análisis

## Solución de Problemas

### "Servicio de detección de anemia no disponible"
- Verifica que el contenedor `anemia-service` esté corriendo
- Revisa logs: `docker-compose logs anemia-service`
- Confirma conectividad entre backend y anemia-service

### "Timeout al procesar imagen"
- La imagen es muy grande o el servicio está sobrecargado
- Intenta con una imagen más pequeña o clara
- Aumenta el timeout en `backend/src/api/vision.py` (línea 54)

### "Análisis de imagen completado" pero sin resultado
- Verifica que la imagen sea válida (JPG/PNG)
- Asegúrate que sea clara y bien iluminada
- Revisa consola del navegador para errores

### Imágenes lentas para procesar
- Normal: el primer análisis puede tardar 15-30 segundos
- Verificaciones posteriores son más rápidas (caché de modelos)
- El servicio está optimizado para producción

## Archivos Modificados

### Frontend
- `components/NewFollowUpForm.tsx`: Integración de predicción con manejo de archivos
- `components/FollowUpResults.tsx`: Tab "Estado Anémico" y presentación de resultados

### Backend
- `backend/src/api/vision.py`: Nuevo endpoint `/predict-anemia`
- `backend/main.py`: Registro del router de vision

### Configuración
- `docker-compose.yml`: Servicio anemia-service (ya existente)

## Ejemplos de Uso

### Ejemplo 1: Hemoglobina por Examen
1. Selecciona infante "Juan, 24 meses"
2. Completa datos antropométricos
3. En Exámenes Complementarios: ingresa "12.5" en Hemoglobina
4. Finaliza seguimiento
5. En resultados, tab "Estado Anémico" muestra: **Normal** (12.5 > 12.0)

### Ejemplo 2: Análisis de Imagen
1. Selecciona infante "María, 18 meses"
2. Completa datos antropométricos
3. En Fotografía Clínica: sube foto clara de ojos
4. Sistema analiza automáticamente → muestra resultado
5. Finaliza seguimiento
6. En resultados ve análisis con recomendaciones

### Ejemplo 3: Ambos (Prioridad Hemoglobina)
1. Selecciona infante "Pedro, 30 meses"
2. Completa datos
3. Ingresa Hemoglobina: "11.2"
4. Sube foto de ojos (opcional)
5. Sistema usa Hemoglobina (11.2 < 12.0) → **Anémico**
6. Foto se ignora (hemoglobina tiene prioridad)

## Consideraciones de Privacidad y Seguridad

- Las imágenes se procesan en tiempo real y no se almacenan
- Solo se guarda la estimación de hemoglobina en la base de datos
- Se recomienda obtener consentimiento antes de fotografiar
- Los datos de anemia se incluyen en reportes PDF

## Futuras Mejoras

- [ ] Historial de estimaciones de hemoglobina por imagen
- [ ] Comparación de tendencias anemia-normalidad
- [ ] Integración con laboratorio para confirmación automática
- [ ] Alertas para casos críticos (Hb < 7.0)
- [ ] Análisis de múltiples fotos para mayor precisión
- [ ] Exportación de métricas de anemia a reportes

---

**Versión**: 1.0.0  
**Última actualización**: 2024  
**Tecnología**: ONNX Runtime, FastAPI, Next.js, React
