# ✅ GUÍA DE VALIDACIÓN: Anemia Detection System

## 🎯 Objetivo
Verificar que toda la integración de detección de anemia funciona correctamente.

---

## ✅ Validación Técnica (Pre-requisitos)

### 1. Verificar Servicios Corriendo
```bash
cd c:\Users\MARIA JOSE\evaluacion-nutricional-publico
docker-compose ps
```

**Resultado esperado:**
```
STATUS: Up X minutes (healthy) para:
- frontend (puerto 3000)
- backend (puerto 8000)
- anemia-service (puerto 8001)
- db (puerto 5432)
```

✅ **Checklist:**
- [ ] Frontend: Healthy
- [ ] Backend: Healthy
- [ ] Anemia Service: Healthy
- [ ] Database: Healthy

---

### 2. Verificar Conectividad Backend → Anemia Service
```powershell
# Desde PowerShell, prueba la conexión
$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get
$response.StatusCode  # Debe ser 200

# Verifica que responda
curl http://localhost:8000/health
```

✅ **Resultado esperado:**
```json
{
  "status": "healthy",
  "service": "nutritional-assessment-api",
  "version": "1.0.0",
  "environment": "development",
  "db": true
}
```

---

### 3. Verificar Archivos Creados/Modificados
```powershell
# Verifica que existan los archivos clave
Test-Path "components/NewFollowUpForm.tsx"      # Debe ser True
Test-Path "components/FollowUpResults.tsx"      # Debe ser True
Test-Path "backend/src/api/vision.py"          # Debe ser True
Test-Path "backend/main.py"                    # Debe ser True
```

✅ **Checklist:**
- [ ] `components/NewFollowUpForm.tsx` existe
- [ ] `components/FollowUpResults.tsx` existe
- [ ] `backend/src/api/vision.py` existe
- [ ] `backend/main.py` actualizado

---

## 🧪 Validación Funcional (Pruebas de Usuario)

### Prueba 1: Crear Seguimiento Sin Datos de Anemia

**Pasos:**
1. Accede a `http://localhost:3000`
2. Inicia sesión (si es necesario)
3. Haz clic en "Nuevo Seguimiento"
4. Selecciona un infante
5. Completa datos antropométricos (peso, talla, etc.)
6. **NO rellenes "Hemoglobina"**
7. **NO subas foto de ojos**
8. Haz clic en "Finalizar Seguimiento"

**Resultado esperado:**
- ✅ Seguimiento se guarda
- ✅ En resultados aparece tab "Estado Anémico"
- ✅ Tab muestra: "Sin información de anemia"

✅ **Checklist:**
- [ ] Formulario acepta guardarse sin anemia
- [ ] Tab "Estado Anémico" aparece
- [ ] Mensaje "sin información" es visible

---

### Prueba 2: Con Hemoglobina (Examen de Sangre)

**Pasos:**
1. "Nuevo Seguimiento" → Selecciona infante **24 meses**
2. Completa datos antropométricos
3. En "Hemoglobina (g/dL)": **ingresa 12.5**
4. **NO subas foto**
5. Finaliza seguimiento

**Resultado esperado:**
- ✅ Estado: **NORMAL** (12.5 ≥ 12.0)
- ✅ Fuente: **Examen de sangre**
- ✅ Muestra umbrales y recomendaciones

**Validaciones adicionales:**
```
Tab "Estado Anémico" debe mostrar:
├─ Fuente: "Examen de sangre" 🟦
├─ Hemoglobina: "12.5 g/dL"
├─ Umbral: "12.0 g/dL" (edad 24 meses)
├─ Resultado: "✅ NORMAL" (verde)
└─ Recomendación: "Mantener buena alimentación"
```

✅ **Checklist:**
- [ ] Hemoglobina se guarda correctamente
- [ ] Clasificación: NORMAL
- [ ] Color: Verde
- [ ] Recomendación visible

---

### Prueba 3: Con Hemoglobina Anémica

**Pasos:**
1. "Nuevo Seguimiento" → Selecciona infante **36 meses**
2. Completa datos
3. En "Hemoglobina": **ingresa 10.5**
4. Finaliza seguimiento

**Resultado esperado:**
- ✅ Estado: **ANÉMICO** (10.5 < 12.0)
- ✅ Color: **Rojo/naranja**
- ✅ Recomendación: "Examen de sangre para confirmar"

**Validaciones:**
```
├─ Hemoglobina: "10.5 g/dL"
├─ Resultado: "🔴 ANÉMICO" (rojo)
├─ Recomendación: "Se recomienda realizar un examen..."
└─ Alimentos: Lista de Fe, etc.
```

✅ **Checklist:**
- [ ] Clasificación: ANÉMICO
- [ ] Color: Rojo
- [ ] Recomendaciones mostradas
- [ ] Alimentos ricos en hierro listados

---

### Prueba 4: Con Fotografía (Sin Hemoglobina)

**Pasos:**
1. Busca imagen de ojo clara (.jpg o .png) ~100-500KB
   - Debe mostrar conjuntiva (parte blanca del ojo)
   - Bien iluminada, sin blur
   
2. "Nuevo Seguimiento" → Selecciona infante **20 meses**
3. Completa datos
4. En "Fotografía Clínica": **sube la imagen**
5. **Espera análisis** ⏳ (puede tardar 5-30s)

**Resultado esperado:**
- ✅ Aparece: "⏳ Analizando imagen..."
- ✅ Después: Resultado con Hb estimada
- ✅ Badge de color (rojo/verde)
- ✅ Muestra recomendación

**Validaciones en tiempo real:**
```
Durante carga:
├─ Loader: Giratorio
├─ Texto: "Analizando imagen..."
└─ Duración: 5-30 segundos

Después:
├─ Hb estimada: Ej "11.2 g/dL"
├─ Umbral: "12.0 g/dL"
├─ Badge: "Anémico" (rojo) o "Normal" (verde)
└─ Recomendación: Automática
```

✅ **Checklist:**
- [ ] Indicador de carga aparece
- [ ] Análisis completa
- [ ] Resultado mostrado correctamente
- [ ] Colores apropiados

---

### Prueba 5: Prioridad (Hemoglobina > Imagen)

**Pasos:**
1. Prepara una imagen de ojo
2. "Nuevo Seguimiento" → Selecciona infante
3. Hemoglobina: **11.5** (bajo, anémico)
4. Fotografía: **Sube imagen**
5. Sistema analiza imagen (ej: resultado "12.5" normal)
6. Finaliza seguimiento

**Resultado esperado:**
- ✅ **Usa Hemoglobina (11.5)**, NO imagen
- ✅ Clasificación: **ANÉMICO** (porque 11.5 < 12.0)
- ✅ Fuente: **Examen de sangre**
- ✅ **Imagen se ignora** (aunque el resultado sería normal)

✅ **Checklist:**
- [ ] Resultado final es ANÉMICO (por Hb)
- [ ] Fuente: "Examen de sangre"
- [ ] No usa resultado de imagen
- [ ] Recomendación correcta

---

### Prueba 6: Ambos Campos = Imagen Ignorada

**Variante:**
- Hemoglobina: **13.0** (normal)
- Foto: **Sube imagen** (que pudiera ser anémica)

**Resultado esperado:**
- ✅ Usa 13.0 (normal)
- ✅ Fotografía **NO se procesa/usa**
- ✅ Resultado: NORMAL (ignorando potencial anemia en imagen)

✅ **Checklist:**
- [ ] Lógica de prioridad funciona
- [ ] Imagen no se usa si hay Hb

---

## 🧩 Validación de UI/UX

### 1. Formulario - Sección "Exámenes Complementarios"
```
Visible: 
├─ Label: "Hemoglobina (g/dL) - Opcional"
├─ Hint: "Si tienes el resultado de un examen de sangre..."
└─ Nota: "Este valor tendrá prioridad sobre la estimación"
```

✅ Checklist:
- [ ] Label visible
- [ ] Hint explicativo
- [ ] Placeholder "12.5"

---

### 2. Formulario - Sección "Fotografía Clínica"
```
Visible:
├─ Título: "Fotografía Clínica para Análisis de Anemia"
├─ Upload: "Foto de ojos (para análisis de Hb)"
├─ Hint: "Sube foto clara de la conjuntiva..."
├─ Loader: Cuando procesa
├─ Resultado: En tiempo real (coloreado)
└─ Botón: "Finalizar Seguimiento"
```

✅ Checklist:
- [ ] Upload widget funciona
- [ ] Instrucciones claras
- [ ] Loader muestra durante análisis
- [ ] Resultado mostrado con colores

---

### 3. Resultados - Tab "Estado Anémico"
```
Visible:
├─ Nueva tab con nombre "Estado Anémico"
├─ 4 tabs totales: Resultados | Estado Anémico | Nutricional | Crecimiento
├─ Contenido por caso:
│  ├─ Sin datos: Mensaje explicativo
│  ├─ Con datos: Tarjetas con métricas
│  ├─ Clasificación grande (ANÉMICO/NORMAL)
│  └─ Recomendaciones clínicas
└─ Colores acordes (rojo/verde)
```

✅ Checklist:
- [ ] Tab aparece en resultados
- [ ] Contenido correcto según datos
- [ ] Colores apropiados
- [ ] Recomendaciones visibles

---

## 📊 Validación de Base de Datos

### 1. Verificar que se guarda `anemia_result`

```sql
-- Conecta a PostgreSQL
-- Busca la tabla de seguimientos

SELECT id_seguimiento, 
       infante_id, 
       hemoglobina,
       -- Si tienes columna para resultado de anemia:
       -- anemia_result, 
       fecha
FROM seguimientos 
ORDER BY fecha DESC 
LIMIT 1;
```

**Resultado esperado:**
```
id_seguimiento | infante_id | hemoglobina | fecha
──────────────┼────────────┼─────────────┼──────
       123    |     45     |    12.5     | 2024-01-15
```

✅ Checklist:
- [ ] Dato de hemoglobina se guarda
- [ ] ID de infante correcto
- [ ] Fecha registrada

---

### 2. Verificar sessionStorage

En la consola del navegador (F12 → Application → Storage → Session Storage):

```javascript
// Debe existir:
sessionStorage.getItem('last_seguimiento_id')
// Resultado: "123" (número)

sessionStorage.getItem('anemia_result')  
// Resultado: '{"source":"hemoglobina","value":12.5,"threshold":12.0,"isAnemic":false,"label":"Normal"}'
```

✅ Checklist:
- [ ] `last_seguimiento_id` guardado
- [ ] `anemia_result` estructura correcta
- [ ] Valores numéricos correctos

---

## 🐛 Debugging

### Si el análisis NO funciona:

1. **Verifica logs del backend:**
```bash
docker-compose logs backend | Select-String "vision\|predict-anemia"
```

2. **Verifica logs del servicio de anemia:**
```bash
docker-compose logs anemia-service | tail -20
```

3. **Prueba endpoint directamente:**
```bash
# Necesitas una imagen válida primero
curl -F "file=@C:\path\to\image.jpg" `
     -F "age_months=24" `
     http://localhost:8000/api/vision/predict-anemia
```

---

## 📋 Checklist Final de Validación

### Técnica
- [ ] Todos servicios corriendo (healthy)
- [ ] Backend conecta con Anemia Service
- [ ] Archivos modificados existentes
- [ ] Sin errores TypeScript

### Funcional - Casos de Uso
- [ ] Prueba 1: Sin anemia (sin datos) - Funciona
- [ ] Prueba 2: Con Hemoglobina normal - Funciona
- [ ] Prueba 3: Con Hemoglobina anémica - Funciona
- [ ] Prueba 4: Con imagen (análisis) - Funciona
- [ ] Prueba 5: Prioridad hemoglobina - Funciona
- [ ] Prueba 6: Ambos (ignora imagen) - Funciona

### UI/UX
- [ ] Formulario claro con instrucciones
- [ ] Loader visible durante análisis
- [ ] Resultados mostrados en tiempo real
- [ ] Tab "Estado Anémico" accesible
- [ ] Colores intuitivos (rojo/verde)
- [ ] Recomendaciones legibles

### Base de Datos
- [ ] Datos se guardan en PostgreSQL
- [ ] sessionStorage tiene valores correctos
- [ ] Campos numéricos almacenados bien

### Documentación
- [ ] `INTEGRACION_ANEMIA.md` existe
- [ ] `RESUMEN_INTEGRACION.md` existe
- [ ] Este archivo: `VALIDACION.md` existe

---

## ✨ Si todo está ✅, la Integración está LISTA

**Felicidades**, el sistema de detección de anemia está 100% funcional.

### Próximos pasos:
1. ✅ Usar en producción
2. 🔄 Monitorear resultados clínicos
3. 📈 Recolectar feedback de usuarios
4. 🎓 Entrenar personal en el nuevo sistema

---

**Fecha de validación**: ________________  
**Usuario**: ________________  
**Resultado**: [ ] ✅ EXITOSA [ ] ❌ CON PROBLEMAS

**Notas adicionales:**
```
__________________________________________________________________________

__________________________________________________________________________

__________________________________________________________________________
```

---

**¡Gracias por usar el Sistema de Evaluación Nutricional!**

