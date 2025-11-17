#!/bin/bash

echo "🚀 Iniciando servicios de Evaluación Nutricional..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Iniciar Backend
echo -e "${BLUE}📊 Iniciando Backend (FastAPI)...${NC}"
cd /workspaces/evaluacion-nutricional-publico/backend
pkill -f "uvicorn src.main:app" 2>/dev/null
sleep 2

DATABASE_URL="postgresql://postgres:wpjKpgZSDCcHcVigyWRkMJDNGVWasGqf@tramway.proxy.rlwy.net:22762/railway" \
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &

sleep 5
echo -e "${GREEN}✅ Backend iniciado en http://localhost:8000${NC}"

# 2. Iniciar Frontend
echo -e "${BLUE}🌐 Iniciando Frontend (Next.js)...${NC}"
cd /workspaces/evaluacion-nutricional-publico
pkill -f "next dev" 2>/dev/null
sleep 2

pnpm dev > /tmp/frontend.log 2>&1 &

sleep 5
echo -e "${GREEN}✅ Frontend iniciado en http://localhost:3000${NC}"

# 3. Verificar servicios
echo ""
echo "🔍 Verificando servicios..."
sleep 3

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend respondiendo correctamente${NC}"
else
    echo -e "❌ Backend no responde"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend respondiendo correctamente${NC}"
else
    echo -e "❌ Frontend no responde"
fi

echo ""
echo "📝 Logs disponibles en:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🔑 Credenciales de administrador:"
echo "   Email: admin@example.com"
echo "   Password: admin123"
echo ""
echo "🌐 Aplicación disponible en: http://localhost:3000"
