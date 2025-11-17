# 🚀 Guía de Inicio Rápido - Sistema de Evaluación Nutricional

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Git

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/MauroPrasca29/evaluacion-nutricional-publico.git
cd evaluacion-nutricional-publico
```

### 2️⃣ Copiar archivo de configuración (opcional)
```bash
cp .env.example .env
# Editar .env si necesitas cambiar contraseñas o puertos
```

### 3️⃣ Iniciar con Docker Compose
```bash
docker-compose up -d
```

¡Eso es todo! El sistema se levantará automáticamente con:
- ✅ Base de datos PostgreSQL con tablas creadas
- ✅ Backend FastAPI corriendo en http://localhost:8000
- ✅ Frontend Next.js corriendo en http://localhost:3000
- ✅ Usuario administrador creado automáticamente
- ✅ Redis para tareas asíncronas
- ✅ Celery worker para procesamiento

## 🔑 Credenciales por Defecto

**Administrador:**
- Email: `admin@example.com`
- Password: `admin123`

**Usuario Normal:**
- Email: `user@example.com`  
- Password: `user123`

## 📊 Servicios Disponibles

| Servicio | Puerto | URL |
|----------|--------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

## 🛠️ Comandos Útiles

### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### Reiniciar servicios
```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend
```

### Detener servicios
```bash
docker-compose down

# Detener y eliminar volúmenes (borra la BD)
docker-compose down -v
```

### Reconstruir después de cambios
```bash
docker-compose up -d --build
```

## 🔧 Desarrollo Local (sin Docker)

### Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variable de entorno
export DATABASE_URL="postgresql://postgres:nutricion2024@localhost:5432/nutricion_db"

# Crear tablas
python create_tables.py

# Crear usuario admin
python ensure_admin.py

# Iniciar servidor
uvicorn src.main:app --reload
```

### Frontend
```bash
# Instalar dependencias
pnpm install

# Iniciar en modo desarrollo
pnpm dev
```

## 📚 Estructura del Proyecto

```
.
├── app/                    # Páginas Next.js (App Router)
├── backend/               # Backend FastAPI
│   ├── src/
│   │   ├── api/          # Endpoints API
│   │   ├── db/           # Modelos y base de datos
│   │   ├── services/     # Lógica de negocio
│   │   └── main.py       # Aplicación principal
│   ├── create_tables.py  # Script para crear tablas
│   └── ensure_admin.py   # Script para crear admin
├── components/           # Componentes React
├── database/            # Scripts SQL iniciales
├── docker-compose.yml   # Configuración Docker
└── .env.example        # Variables de entorno ejemplo
```

## 🔐 Seguridad

⚠️ **IMPORTANTE para Producción:**
1. Cambiar `SECRET_KEY` en `.env`
2. Cambiar contraseñas de PostgreSQL
3. Cambiar password del admin en la BD
4. Usar HTTPS
5. Configurar CORS apropiadamente

## 🐛 Solución de Problemas

### El backend no arranca
```bash
# Ver logs del backend
docker-compose logs backend

# Verificar que PostgreSQL esté listo
docker-compose logs db
```

### Error de conexión a la base de datos
```bash
# Verificar que db esté saludable
docker-compose ps

# Reiniciar base de datos
docker-compose restart db
```

### Puerto ya en uso
```bash
# Cambiar puertos en docker-compose.yml
# Por ejemplo, cambiar "3000:3000" a "3001:3000"
```

## 📞 Soporte

Para reportar problemas o sugerencias, crear un issue en:
https://github.com/MauroPrasca29/evaluacion-nutricional-publico/issues

---

**¡Listo para empezar!** 🎉
