# Sistema de Evaluación Nutricional Infantil

Sistema completo para la evaluación y seguimiento nutricional de niños, desarrollado con Next.js 15, FastAPI y PostgreSQL.

## 🚀 Inicio Rápido con Docker (3 pasos)

### Prerrequisitos
- Docker y Docker Compose instalados
- Git

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/MauroPrasca29/evaluacion-nutricional-publico.git
cd evaluacion-nutricional-publico
```

2. **Levantar todos los servicios**
```bash
docker-compose up -d
```

3. **Verificar que todo funcione**
```bash
./verify-system.sh
```

¡Eso es todo! El sistema se configura automáticamente con:
- ✅ Base de datos PostgreSQL con tablas creadas
- ✅ Usuario administrador listo para usar
- ✅ Backend y Frontend corriendo
- ✅ Datos de ejemplo cargados

### 🌐 Servicios Disponibles

| Servicio | Puerto | URL |
|----------|--------|-----|
| **Frontend** | 3000 | http://localhost:3000 |
| **Backend API** | 8000 | http://localhost:8000 |
| **API Docs** | 8000 | http://localhost:8000/docs |
| **PostgreSQL** | 5432 | localhost:5432 |
| **Redis** | 6379 | localhost:6379 |

### 🔑 Credenciales por Defecto

**Administrador:**
- Email: `admin@example.com`
- Password: `admin123`

**Usuario Normal:**
- Email: `user@example.com`
- Password: `user123`

**Base de Datos:**
- Host: `localhost:5432`
- Database: `nutricion_db`
- User: `postgres`
- Password: `nutricion2024`

> ⚠️ **IMPORTANTE:** Cambiar estas credenciales en producción editando el archivo `.env`

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
