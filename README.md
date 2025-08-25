# Sistema de Evaluación Nutricional Infantil

Sistema completo para la evaluación y seguimiento nutricional de niños en comunidades vulnerables.

## Estructura del Proyecto

\`\`\`
📦 nutricional-infantil/
│
├── 📁 app/                      # Frontend con Next.js
├── 📁 backend/                  # Backend con FastAPI
├── 📁 database/                 # Gestión de la base de datos
├── 📁 infra/                    # Infraestructura
├── 📁 components/               # Componentes UI de React/Next.js
├── 📁 data/                     # Estándares OMS y datos mock
├── 📁 lib/                      # Librerías y utilidades
├── 📁 public/                   # Archivos estáticos
├── 📁 styles/                   # Estilos adicionales
├── 📁 types/                    # Tipos e interfaces TypeScript
└── 📁 utils/                    # Funciones utilitarias
\`\`\`

## Instalación

### Desarrollo Local

1. **Frontend (Next.js)**
\`\`\`bash
npm install
npm run dev
\`\`\`

2. **Backend (FastAPI)**
\`\`\`bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
\`\`\`

3. **Base de Datos (PostgreSQL)**
\`\`\`bash
# Configurar PostgreSQL localmente
# Ejecutar migrations
\`\`\`

### Con Docker

\`\`\`bash
docker-compose up -d
\`\`\`

## Funcionalidades

- ✅ Gestión de niños y perfiles
- ✅ Evaluaciones nutricionales completas
- ✅ Gráficos de crecimiento
- ✅ Sistema de alertas
- ✅ Reportes y estadísticas
- ✅ Importación de datos Excel
- ✅ Interfaz responsive

## Tecnologías

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python, SQLAlchemy, Pydantic
- **Base de Datos**: PostgreSQL
- **Infraestructura**: Docker, Nginx, Kubernetes

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

MIT License
