# Sistema de Evaluación Nutricional Infantil

Sistema completo para la evaluación y seguimiento del estado nutricional de niños en comunidades vulnerables.

## Estructura del Proyecto

\`\`\`
📦 nutricional-infantil/
├── 📁 frontend/          # Next.js 13+ Application
├── 📁 backend/           # FastAPI Backend
├── 📁 database/          # PostgreSQL Scripts
└── 📁 infra/            # Infrastructure & Deployment
\`\`\`

## Tecnologías

### Frontend
- **Next.js 13+** con App Router
- **TypeScript** para tipado fuerte
- **Tailwind CSS** para estilos
- **shadcn/ui** para componentes
- **Recharts** para gráficos

### Backend
- **FastAPI** para API REST
- **SQLAlchemy** para ORM
- **PostgreSQL** como base de datos
- **JWT** para autenticación
- **OpenCV** para procesamiento de imágenes
- **Pandas** para procesamiento de Excel

### Infrastructure
- **Docker** para containerización
- **Docker Compose** para desarrollo
- **Nginx** como reverse proxy
- **Kubernetes** para producción

## Instalación y Desarrollo

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+

### Desarrollo Local

1. **Clonar el repositorio**
\`\`\`bash
git clone <repository-url>
cd nutricional-infantil
\`\`\`

2. **Configurar Frontend**
\`\`\`bash
npm install
npm run dev
\`\`\`

3. **Configurar Backend**
\`\`\`bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
\`\`\`

4. **Configurar Base de Datos**
\`\`\`bash
# Crear base de datos
createdb nutritional_db

# Ejecutar migraciones
psql -d nutritional_db -f database/schema.sql
psql -d nutritional_db -f database/seeds.sql
\`\`\`

### Desarrollo con Docker

\`\`\`bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down
\`\`\`

## Funcionalidades

### ✅ Implementadas
- Dashboard con estadísticas globales
- Gestión de niños y perfiles
- Formularios de seguimiento nutricional
- Gráficos de crecimiento
- Sistema de alertas
- Importación de datos Excel
- Reportes y estadísticas

### 🚧 En Desarrollo
- API Backend completa
- Autenticación JWT
- Base de datos PostgreSQL
- Procesamiento de imágenes ML
- Generación de PDFs
- Notificaciones push

### 📋 Por Implementar
- Modo offline
- Sincronización de datos
- Backup automático
- Análisis predictivo
- Dashboard administrativo

## API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `GET /api/auth/me` - Obtener usuario actual

### Niños
- `GET /api/children` - Listar niños
- `POST /api/children` - Crear niño
- `GET /api/children/{id}` - Obtener niño
- `PUT /api/children/{id}` - Actualizar niño
- `DELETE /api/children/{id}` - Eliminar niño

### Seguimientos
- `GET /api/followups` - Listar seguimientos
- `POST /api/followups` - Crear seguimiento
- `GET /api/followups/{id}` - Obtener seguimiento
- `GET /api/followups/child/{id}` - Seguimientos por niño

### Reportes
- `GET /api/reports/statistics` - Estadísticas globales
- `GET /api/reports/pdf/{id}` - Generar PDF
- `GET /api/reports/export` - Exportar datos

### Importación
- `POST /api/import/excel` - Importar Excel
- `GET /api/import/template` - Descargar plantilla
- `GET /api/import/status/{id}` - Estado de importación

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Contacto

- **Proyecto**: Sistema de Evaluación Nutricional Infantil
- **Versión**: 1.0.0
- **Estado**: En Desarrollo Activo
