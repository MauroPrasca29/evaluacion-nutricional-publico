#!/usr/bin/env bash
# verificar-instalacion.sh - Script para verificar que la instalación es correcta

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔍 VERIFICACIÓN DE INSTALACIÓN - SERVICIO DE ANEMIA      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Contador
PASSED=0
FAILED=0

check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (falta: $file)"
        ((FAILED++))
    fi
}

check_directory() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (falta: $dir)"
        ((FAILED++))
    fi
}

check_command() {
    local cmd=$1
    local description=$2
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    fi
}

# Verificaciones
echo -e "${BLUE}Verificando archivos necesarios...${NC}"
echo ""

check_directory "anemia-service" "Directorio anemia-service existe"
check_file "anemia-service/main.py" "Archivo main.py existe"
check_file "anemia-service/requirements.txt" "Archivo requirements.txt existe"
check_file "anemia-service/test_service.py" "Archivo test_service.py existe"
check_file "anemia-service/README.md" "Archivo README.md existe"
check_file "anemia-service/.gitignore" "Archivo .gitignore existe"

echo ""
echo -e "${BLUE}Verificando Dockerfile...${NC}"
echo ""

check_file "Dockerfile.anemia" "Dockerfile.anemia existe"
check_file "Dockerfile.anemia" "Usa python:3.11-slim"
check_file "Dockerfile.anemia" "Incluye huggingface-hub"

echo ""
echo -e "${BLUE}Verificando docker-compose.yml...${NC}"
echo ""

if grep -q "anemia-service:" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Servicio anemia-service definido"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Servicio anemia-service NO encontrado"
    ((FAILED++))
fi

if grep -q "redis:" docker-compose.yml; then
    echo -e "${RED}✗${NC} Redis aún definido (debe ser eliminado)"
    ((FAILED++))
else
    echo -e "${GREEN}✓${NC} Redis eliminado correctamente"
    ((PASSED++))
fi

if grep -q "celery" docker-compose.yml; then
    echo -e "${RED}✗${NC} Celery referencias encontradas (debe ser eliminado)"
    ((FAILED++))
else
    echo -e "${GREEN}✓${NC} Celery eliminado correctamente"
    ((PASSED++))
fi

echo ""
echo -e "${BLUE}Verificando backend...${NC}"
echo ""

if grep -q "httpx" backend/src/api/vision_anemia_onnx.py; then
    echo -e "${GREEN}✓${NC} Backend usa httpx para proxy"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Backend no usa httpx"
    ((FAILED++))
fi

if grep -q "ANEMIA_ASYNC" backend/src/api/vision_anemia_onnx.py; then
    echo -e "${RED}✗${NC} ANEMIA_ASYNC aún encontrado (debe ser eliminado)"
    ((FAILED++))
else
    echo -e "${GREEN}✓${NC} ANEMIA_ASYNC eliminado"
    ((PASSED++))
fi

echo ""
echo -e "${BLUE}Verificando documentación...${NC}"
echo ""

check_file "CAMBIOS.md" "Documento CAMBIOS.md existe"
check_file "ANEMIA_QUICKSTART.md" "Documento ANEMIA_QUICKSTART.md existe"
check_file "INSTRUCCIONES_EJECUCION.md" "Documento INSTRUCCIONES_EJECUCION.md existe"
check_file "ESTRUCTURA_FINAL.txt" "Documento ESTRUCTURA_FINAL.txt existe"

echo ""
echo -e "${BLUE}Verificando herramientas instaladas...${NC}"
echo ""

check_command "docker" "Docker instalado"
check_command "docker-compose" "Docker Compose instalado"

echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  📊 RESUMEN DE VERIFICACIÓN                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Verificaciones exitosas: ${GREEN}$PASSED${NC}"
echo -e "Verificaciones fallidas: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ TODAS LAS VERIFICACIONES PASARON                       ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║  El servicio de anemia está correctamente configurado      ║${NC}"
    echo -e "${GREEN}║  Puedes proceder a ejecutar: docker-compose up -d          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ ALGUNAS VERIFICACIONES FALLARON                        ║${NC}"
    echo -e "${RED}║                                                            ║${NC}"
    echo -e "${RED}║  Revisa los archivos marcados arriba                       ║${NC}"
    echo -e "${RED}║  y asegúrate de que están en su lugar                      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
