# Sistema de Evaluación Nutricional Infantil

Sistema completo para la evaluación y seguimiento del estado nutricional de niños en comunidades vulnerables, desarrollado con Next.js (frontend) y FastAPI (backend).

## 🚀 Características Principales

### Frontend (Next.js)
- **Dashboard interactivo** con estadísticas en tiempo real
- **Gestión completa de niños** con perfiles detallados
- **Formularios de evaluación** nutricional completos
- **Gráficos de crecimiento** basados en estándares OMS
- **Sistema de alertas** automáticas
- **Importación masiva** de datos desde Excel
- **Generación de reportes** en PDF
- **Interfaz responsive** adaptable a móviles y tablets

### Backend (FastAPI)
- **API RESTful** completa con documentación automática
- **Autenticación JWT** con roles de usuario
- **Base de datos PostgreSQL** con migraciones Alembic
- **Procesamiento de imágenes** con OpenCV
- **Análisis nutricional** automatizado
- **Sistema de notificaciones** y alertas
- **Caching con Redis** para mejor rendimiento

## 🏗️ Arquitectura del Sistema

\`\`\`
📦 nutricional-infantil/
├── 📁 app/                      # Frontend Next.js
├── 📁 backend/                  # Backend FastAPI
├── 📁 database/                 # Scripts PostgreSQL
├── 📁 infra/                    # Docker & Kubernetes
├── 📁 components/               # Componentes React
├── 📁 data/                     # Datos y estándares OMS
└── 📁 types/                    # Tipos TypeScript
\`\`\`

## 🛠️ Tecnologías Utilizadas

### Frontend
- **Next.js 14** - Framework React con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework de estilos
- **shadcn/ui** - Componentes UI
- **Recharts** - Gráficos interactivos
- **React Hook Form** - Manejo de formularios

### Backend
- **FastAPI** - Framework web moderno para Python
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **PostgreSQL** - Base de datos relacional
- **Redis** - Cache y sesiones
- **OpenCV** - Procesamiento de imágenes
- **Pandas** - Análisis de datos

### Infraestructura
- **Docker** - Contenedorización
- **Docker Compose** - Orquestación local
- **Nginx** - Reverse proxy
- **Kubernetes** - Orquestación en producción

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)
- PostgreSQL 15+ (para desarrollo local)

### Instalación con Docker (Recomendado)

1. **Clonar el repositorio**
\`\`\`bash
git clone <repository-url>
cd nutricional-infantil
\`\`\`

2. **Configurar variables de entorno**
\`\`\`bash
cp .env.example .env
# Editar .env con tus configuraciones
\`\`\`

3. **Levantar los servicios**
\`\`\`bash
cd infra
docker-compose up -d
\`\`\`

4. **Verificar que los servicios estén funcionando**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Nginx: http://localhost:80

### Instalación para Desarrollo Local

#### Frontend
\`\`\`bash
npm install
npm run dev
\`\`\`

#### Backend
\`\`\`bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
\`\`\`

#### Base de Datos
\`\`\`bash
# Crear base de datos
createdb nutritional_db

# Ejecutar migraciones
cd database
psql -d nutritional_db -f schema.sql
psql -d nutritional_db -f seeds.sql
\`\`\`

## 📊 Funcionalidades del Sistema

### 1. Dashboard Principal
- Estadísticas globales (total niños, alertas, evaluaciones pendientes)
- Gráfico de distribución de IMC por grupos de edad
- Lista de próximos seguimientos
- Actividad reciente del sistema

### 2. Gestión de Niños
- Registro completo de nuevos niños
- Búsqueda y filtrado avanzado
- Perfiles individuales con historial completo
- Gráficos de crecimiento personalizados

### 3. Evaluaciones Nutricionales
- Formularios completos de seguimiento
- Mediciones antropométricas
- Documentación fotográfica
- Análisis automático y recomendaciones

### 4. Sistema de Alertas
- Detección automática de riesgos nutricionales
- Clasificación por niveles de prioridad
- Notificaciones en tiempo real
- Seguimiento de resolución

### 5. Reportes y Estadísticas
- Reportes individuales en PDF
- Estadísticas poblacionales
- Análisis de tendencias
- Exportación de datos

### 6. Importación de Datos
- Carga masiva desde archivos Excel
- Validación automática de datos
- Reporte de errores y advertencias
- Plantillas descargables

## 🔧 Configuración

### Variables de Entorno

#### Backend (.env)
\`\`\`env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/nutritional_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0

# File uploads
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
\`\`\`

#### Frontend (.env.local)
\`\`\`env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema Nutricional Infantil
\`\`\`

## 🧪 Testing

### Backend Tests
\`\`\`bash
cd backend
pytest
pytest --cov=src tests/
\`\`\`

### Frontend Tests
\`\`\`bash
npm test
npm run test:coverage
\`\`\`

## 📚 API Documentation

La documentación completa de la API está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario
- `POST /auth/refresh` - Renovar token

#### Niños
- `GET /children` - Listar niños
- `POST /children` - Crear nuevo niño
- `GET /children/{id}` - Obtener niño por ID
- `PUT /children/{id}` - Actualizar niño

#### Seguimientos
- `GET /followups` - Listar seguimientos
- `POST /followups` - Crear nuevo seguimiento
- `GET /followups/{id}` - Obtener seguimiento por ID

#### Reportes
- `GET /reports/child/{id}` - Reporte individual
- `GET /reports/statistics` - Estadísticas globales
- `POST /reports/generate` - Generar reporte personalizado

## 🚢 Despliegue

### Docker Compose (Producción)
\`\`\`bash
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

### Kubernetes
\`\`\`bash
kubectl apply -f infra/k8s/
\`\`\`

### Variables de Producción
- Configurar certificados SSL
- Actualizar CORS origins
- Configurar backup de base de datos
- Configurar monitoreo y logs

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo de Desarrollo

- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI, PostgreSQL, Redis
- **DevOps**: Docker, Kubernetes, Nginx

## 📞 Soporte

Para soporte técnico o preguntas sobre el sistema:
- Email: soporte@nutricional.com
- Documentación: [Wiki del proyecto]
- Issues: [GitHub Issues]

---

**Sistema de Evaluación Nutricional Infantil v1.0.0**
*Desarrollado para mejorar la salud nutricional de niños en comunidades vulnerables*
