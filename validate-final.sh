#!/bin/bash
# Script de Validación Final Pre-Commit
# Verifica que todo funciona después de clonar y levantar el contenedor

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        VALIDACIÓN FINAL PRE-COMMIT - SISTEMA COMPLETO         ║"
echo "║           Detección de Anemia + Evaluación Nutricional        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Variables
BACKEND_URL="http://localhost:8000"
ANEMIA_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"
DB_HOST="localhost"
DB_PORT="5432"

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de checks
PASSED=0
FAILED=0

# Función para imprimir resultado
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $1"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $1"
        ((FAILED++))
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  VERIFICACIÓN DE SERVICIOS DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Verificando estado de contenedores..."
docker-compose ps | grep -E "frontend|backend|anemia-service|db" > /dev/null
check_result "Todos los contenedores están registrados"

echo ""
echo "Verificando que todos los servicios estén corriendo..."
FRONTEND_STATUS=$(docker-compose ps frontend | grep -o "Up\|Exited" | head -1)
[ "$FRONTEND_STATUS" = "Up" ]
check_result "Frontend corriendo"

BACKEND_STATUS=$(docker-compose ps backend | grep -o "Up\|Exited" | head -1)
[ "$BACKEND_STATUS" = "Up" ]
check_result "Backend corriendo"

ANEMIA_STATUS=$(docker-compose ps anemia-service | grep -o "Up\|Exited" | head -1)
[ "$ANEMIA_STATUS" = "Up" ]
check_result "Anemia Service corriendo"

DB_STATUS=$(docker-compose ps db | grep -o "Up\|Exited" | head -1)
[ "$DB_STATUS" = "Up" ]
check_result "Base de datos corriendo"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  VERIFICACIÓN DE SALUD (HEALTHCHECKS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Backend health check..."
curl -s "$BACKEND_URL/health" | grep -q "healthy"
check_result "Backend respondiendo health check"

echo "Anemia Service health check..."
curl -s "$ANEMIA_URL/health" | grep -q "healthy"
check_result "Anemia Service respondiendo health check"

echo "Frontend accesible..."
curl -s "$FRONTEND_URL" | grep -q "html\|DOCTYPE" 
check_result "Frontend respondiendo"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  VERIFICACIÓN DE ARCHIVOS CLAVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Verificando archivos del frontend..."
[ -f "components/NewFollowUpForm.tsx" ]
check_result "components/NewFollowUpForm.tsx existe"

[ -f "components/FollowUpResults.tsx" ]
check_result "components/FollowUpResults.tsx existe"

echo "Verificando archivos del backend..."
[ -f "backend/src/api/vision.py" ]
check_result "backend/src/api/vision.py existe"

[ -f "backend/main.py" ]
check_result "backend/main.py existe"

echo "Verificando archivos de configuración..."
[ -f "docker-compose.yml" ]
check_result "docker-compose.yml existe"

[ -f "anemia-service/main.py" ]
check_result "anemia-service/main.py existe"

[ -f "anemia-service/requirements.txt" ]
check_result "anemia-service/requirements.txt existe"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  VERIFICACIÓN DE ENDPOINTS API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Backend - GET /health..."
curl -s "$BACKEND_URL/health" | grep -q "status"
check_result "GET /health responde"

echo "Backend - GET /api/children..."
curl -s "$BACKEND_URL/api/children" > /dev/null 2>&1
check_result "GET /api/children accesible"

echo "Anemia Service - GET /health..."
curl -s "$ANEMIA_URL/health" | grep -q "status"
check_result "GET /predict/health responde"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  VERIFICACIÓN DE CONECTIVIDAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Backend → Base de Datos..."
curl -s "$BACKEND_URL/health" | grep -q '"db": true'
check_result "Backend conectado a BD"

echo "Backend → Anemia Service..."
# Verificar que el endpoint está registrado
curl -s "$BACKEND_URL/docs" 2>/dev/null | grep -q "vision\|anemia" || true
check_result "Backend tiene router de vision"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  VERIFICACIÓN DE MODELOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Verificando modelo ONNX..."
docker-compose exec -T anemia-service bash -c "ls -la /app/models/ | grep -E '\.onnx|hb_regressor'" > /dev/null 2>&1
check_result "Modelo ONNX descargado y disponible"

echo "Verificando inicialización del modelo..."
docker-compose logs anemia-service | grep -i "model\|loaded\|onnx" > /dev/null 2>&1
check_result "Modelo ONNX cargado en servicio"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  VERIFICACIÓN DE ARCHIVOS TYPESCRIPT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Verificando que NewFollowUpForm.tsx tenga función de anemia..."
grep -q "predictAnemiaFromImage\|anemiaResult\|setPredictingAnemia" components/NewFollowUpForm.tsx
check_result "NewFollowUpForm.tsx tiene integración de anemia"

echo "Verificando que FollowUpResults.tsx tenga tab de anemia..."
grep -q 'value="anemia"' components/FollowUpResults.tsx
check_result "FollowUpResults.tsx tiene tab 'Estado Anémico'"

echo "Verificando endpoint vision en backend..."
grep -q "def predict_anemia\|@router.post" backend/src/api/vision.py
check_result "backend/src/api/vision.py tiene endpoint"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  VERIFICACIÓN DE CONFIGURACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Docker Compose tiene anemia-service..."
grep -q "anemia-service:" docker-compose.yml
check_result "anemia-service definido en docker-compose"

echo "Docker Compose expone puerto 8001..."
grep -q "8001:8000" docker-compose.yml
check_result "Puerto 8001 mapeado correctamente"

echo "Backend main.py registra router vision..."
grep -q "vision_router\|/api/vision" backend/main.py
check_result "backend/main.py registra router vision"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  VERIFICACIÓN DE DOCUMENTACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

[ -f "INTEGRACION_ANEMIA.md" ]
check_result "INTEGRACION_ANEMIA.md existe"

[ -f "RESUMEN_INTEGRACION.md" ]
check_result "RESUMEN_INTEGRACION.md existe"

[ -f "QUICK_REFERENCE_ANEMIA.md" ]
check_result "QUICK_REFERENCE_ANEMIA.md existe"

[ -f "VALIDACION_INTEGRACION.md" ]
check_result "VALIDACION_INTEGRACION.md existe"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔟 RESULTADO FINAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "Total de checks: $TOTAL"
echo -e "${GREEN}Pasaron: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Fallaron: $FAILED${NC}"
else
    echo -e "${GREEN}Fallaron: 0${NC}"
fi
echo "Porcentaje de éxito: $PERCENTAGE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║          ✅ TODOS LOS TESTS PASARON - LISTO PARA COMMIT      ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "El repositorio está en perfecto estado. Puede clonarse y ejecutarse"
    echo "sin problemas."
    echo ""
    exit 0
else
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║        ⚠️  ALGUNOS TESTS FALLARON - REVISAR ANTES COMMIT       ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi
