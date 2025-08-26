# Sistema de Evaluación Nutricional Infantil

Sistema completo para la evaluación y seguimiento nutricional de niños, desarrollado con Next.js, FastAPI y PostgreSQL.

## 🚀 Inicio Rápido con Docker

### Prerrequisitos
- Docker y Docker Compose instalados
- Git

### Instalación

1. **Clonar el repositorio**
\`\`\`bash
git clone <repository-url>
cd nutricional-infantil
\`\`\`

2. **Levantar los servicios**
\`\`\`bash
cd infra
docker-compose up -d
\`\`\`

3. **Verificar que los servicios estén funcionando**
\`\`\`bash
docker-compose ps
\`\`\`

### 🌐 Servicios Disponibles

- **Frontend (Next.js)**: http://localhost:3000
- **Backend API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx Proxy**: http://localhost:80
- **PostgreSQL**: localhost:5432

### 📊 Credenciales por Defecto

**Administrador:**
- Email: admin@nutricion.com
- Password: password123

**Base de Datos:**
- Host: localhost:5432
- Database: nutritional_db
- User: postgres
- Password: nutritional_password_2024

## 🛠️ Desarrollo Local

### Frontend (Next.js)
\`\`\`bash
npm install
npm run dev
\`\`\`

### Backend (FastAPI)
\`\`\`bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
\`\`\`

## 📁 Estructura del Proyecto

\`\`\`
nutricional-infantil/
├── app/                    # Next.js pages
├── components/             # React components
├── backend/               # FastAPI backend
├── database/              # SQL schemas and seeds
├── infra/                 # Docker configuration
├── public/                # Static assets
└── types/                 # TypeScript definitions
\`\`\`

## 🐳 Comandos Docker Útiles

\`\`\`bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache
\`\`\`

## 🔧 Configuración

### Variables de Entorno

El sistema utiliza las siguientes variables de entorno:

**Backend:**
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `SECRET_KEY`: Clave secreta para JWT
- `ENVIRONMENT`: development/production

**Frontend:**
- `NEXT_PUBLIC_API_URL`: URL del backend API
- `NEXT_PUBLIC_APP_NAME`: Nombre de la aplicación

## 📈 Funcionalidades

- ✅ Gestión de niños y perfiles
- ✅ Evaluaciones nutricionales
- ✅ Gráficos de crecimiento WHO
- ✅ Sistema de alertas
- ✅ Reportes y estadísticas
- ✅ Importación de datos Excel
- ✅ Dashboard interactivo
- ✅ Múltiples sedes/ubicaciones

## 🔒 Seguridad

- Autenticación JWT
- Validación de datos con Pydantic
- CORS configurado
- Rate limiting en Nginx
- Usuarios no-root en contenedores

## 📝 API Documentation

La documentación completa de la API está disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.
