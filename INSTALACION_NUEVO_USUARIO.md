# GUÍA DE INSTALACIÓN PARA NUEVOS USUARIOS

## Paso a Paso: Desde Clone Hasta Funcionando

### Requisitos Previos
- Docker y Docker Compose instalados
- Puertos disponibles: 3000, 5432, 8000, 8001
- Al menos 4GB RAM libres
- 2-3 minutos de espera inicial

---

## 1️⃣ CLONAR Y PREPARAR

```bash
# Clonar repositorio
git clone https://github.com/MauroPrasca29/evaluacion-nutricional-publico.git
cd evaluacion-nutricional-publico

# Verificar estructura
ls -la
# Debe ver: anemia-service/, backend/, components/, docker-compose.yml, etc.
```

---

## 2️⃣ LEVANTAR LOS SERVICIOS

```bash
# Iniciar todos los contenedores
docker-compose up -d

# Ver que estén corriendo (esperar 10-30 segundos para que inicien)
docker-compose ps

# Debería ver algo así:
# NAME              SERVICE         STATUS      PORTS
# nutricion_frontend    frontend        Up (healthy)   0.0.0.0:3000->3000/tcp
# nutricion_backend     backend         Up (healthy)   0.0.0.0:8000->8000/tcp
# anemia_service        anemia-service  Up (healthy)   0.0.0.0:8001->8000/tcp
# nutricion_db          db              Up (healthy)   0.0.0.0:5432->5432/tcp
```

---

## 3️⃣ ESPERAR INICIALIZACIÓN

Esperar 1-2 minutos a que:
- Base de datos complete inicialización
- Modelos ONNX se carguen
- Endpoints estén listos

```bash
# Verificar salud del backend (repetir hasta que responda "ok")
curl http://localhost:8000/health
# Expected: {"ok":true,"db":true}

# Verificar salud de anemia service
curl http://localhost:8001/health
# Expected: {"status":"healthy"}
```

---

## 4️⃣ CREAR USUARIO ADMIN (Opcional pero recomendado)

```bash
# Crear usuario administrador
docker-compose exec backend python ensure_admin.py

# El sistema ya tiene usuarios de prueba, pero si necesitas admin:
# Usuario: admin
# Contraseña: admin123
```

---

## 5️⃣ ACCEDER A LA APLICACIÓN

Abre tu navegador en:

```
http://localhost:3000
```

### Usuarios de prueba disponibles:
- **Admin:** admin / admin123
- **Nutricionista:** nutricionista / nutricionista123

---

## 6️⃣ VERIFICAR QUE TODO FUNCIONA

### Test 1: Crear un niño
1. Ir a "Gestión de Niños"
2. Crear nuevo niño
3. Llenar datos básicos
4. Guardar

### Test 2: Crear Follow-up con Anemia Detection
1. En el niño, ir a "Crear Seguimiento"
2. (NUEVO) Subir foto - el sistema predicirá automáticamente
3. Llenar datos de evaluación
4. Guardar

### Test 3: Ver Informe Completo
1. En el niño, ver seguimientos
2. Ver informe más reciente
3. **IMPORTANTE:** Debe tener 4 tabs:
   - Resultados (antropométrico)
   - Estado Anémico (NEW - predicción del modelo)
   - Nutricional (recomendaciones)
   - Crecimiento (gráficos WHO)

---

## 📡 ENDPOINTS DISPONIBLES

### Frontend
```
http://localhost:3000/
```

### Backend API
```
GET  http://localhost:8000/health
GET  http://localhost:8000/api/children
POST http://localhost:8000/api/vision/predict-anemia  (nueva!)
```

### Anemia Service (ONNX)
```
GET  http://localhost:8001/health
POST http://localhost:8001/predict
```

### Base de Datos
```
Host:     localhost
Port:     5432
Database: db_sistema_nutricion
```

---

## 🐛 TROUBLESHOOTING

### Los servicios no inician
```bash
# Ver logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs anemia-service
docker-compose logs db

# Reiniciar servicios
docker-compose restart
```

### Puerto ya en uso
```bash
# Encontrar qué usa el puerto
lsof -i :3000  # para verificar puerto 3000

# Si quieres cambiar puerto en docker-compose.yml:
# Cambia: "3000:3000" por "3001:3000"
```

### Base de datos no se conecta
```bash
# Esperar más tiempo (puede tardar 2-3 minutos)
docker-compose logs db

# Si el error persiste:
docker-compose down -v
docker-compose up -d
```

### Anemia Service no responde
```bash
# Verificar que el modelo se descargó
docker-compose exec anemia-service ls -la /app/models/

# Ver logs del servicio
docker-compose logs anemia-service

# Si falla, reiniciar:
docker-compose restart anemia-service
```

---

## 🔧 CONFIGURACIÓN

### Variables de Entorno (Ya Configuradas)
- `ANEMIA_SERVICE_URL=http://anemia-service:8000`
- `DATABASE_URL=postgresql://postgres:postgres@db:5432/db_sistema_nutricion`
- `NEXT_PUBLIC_API_URL=http://localhost:8000`

No necesitas cambiarlas a menos que personalices el setup.

---

## 📊 LO QUE VAS A VER

### Pantalla Principal
- Dashboard con estadísticas
- Gráficos de IMC global
- Alertas nutricionales

### Gestión de Niños
- Crear nuevos niños
- Ver perfil de cada niño
- Historial de seguimientos

### Crear Seguimiento (Nuevo!)
1. Sube foto (sistema predice anemia automáticamente)
2. Ingresa datos de evaluación
3. El sistema genera informe con 4 tabs

### Informe de Seguimiento (Nuevo!)
Mismo informe anterior pero ahora con tab "Estado Anémico" que muestra:
- Estimación de hemoglobina
- Clasificación de anemia
- Recomendaciones clínicas

---

## ✨ CARACTERÍSTICAS NUEVAS (Este Commit)

1. **Detección Automática de Anemia**
   - Sube foto → Sistema predice hemoglobina
   - Usa modelo ONNX (sin dependencias de PyTorch/Google Drive)
   - Resultado en tiempo real

2. **Tab "Estado Anémico" en Reportes**
   - Muestra estimación de Hb
   - Clasificación: Normal/Leve/Moderada/Severa
   - Recomendaciones personalizadas

3. **Prioridad de Datos**
   - Si ingresaste hemoglobina manualmente → Usa ese valor
   - Si no → Usa predicción del modelo

4. **100% Backward Compatible**
   - Todos los reportes antiguos funcionan igual
   - Funcionalidad nutricional sin cambios
   - Gráficos de crecimiento intactos

---

## 📞 SOPORTE

Si algo no funciona:

1. Revisar logs: `docker-compose logs`
2. Verificar puertos: `docker-compose ps`
3. Reiniciar: `docker-compose restart`
4. Nuclear option: `docker-compose down -v && docker-compose up -d`

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Docker containers están corriendo (docker-compose ps)
- [ ] Backend responde (curl http://localhost:8000/health)
- [ ] Anemia service responde (curl http://localhost:8001/health)
- [ ] Aplicación carga (http://localhost:3000)
- [ ] Puedo loguearme
- [ ] Puedo crear un niño
- [ ] Puedo crear un seguimiento
- [ ] Puedo ver informe con 4 tabs
- [ ] Tab "Estado Anémico" muestra datos

Si todo ✅ **¡Sistema funcionando perfectamente!**

---

## 🎉 ¡LISTO!

Ahora tienes un sistema completo de:
- **Evaluación Nutricional** - Análisis antropométrico, clasificación, recomendaciones
- **Detección de Anemia** - Predicción automática desde foto, clasificación
- **Gestión de Crecimiento** - Gráficos WHO, percentiles, tendencias
- **Base de Datos** - Historial completo de todos los seguimientos

Todo en Docker, listo para producción.

**Próximo paso:** Customiza según tus necesidades o deploya a producción.
