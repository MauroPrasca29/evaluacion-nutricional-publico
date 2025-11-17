#!/bin/bash

# Script de verificación del sistema
# Ejecutar después de docker-compose up -d

echo "🔍 Verificando Sistema de Evaluación Nutricional..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar si un servicio responde
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "Verificando $name... "
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ FALLÓ${NC}"
    return 1
}

# 1. Verificar Backend
if check_service "http://localhost:8000/health" "Backend (FastAPI)"; then
    BACKEND_OK=true
else
    BACKEND_OK=false
fi

# 2. Verificar Frontend
if check_service "http://localhost:3000" "Frontend (Next.js)"; then
    FRONTEND_OK=true
else
    FRONTEND_OK=false
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. Test de Login
if [ "$BACKEND_OK" = true ]; then
    echo "🔐 Probando autenticación..."
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"correo": "admin@example.com", "contrasena": "admin123"}' 2>/dev/null)
    
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
    
    if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
        echo -e "   ${GREEN}✅ Login funcionando${NC}"
        
        # Verificar usuario
        USER_INFO=$(curl -s http://localhost:8000/api/auth/me \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        NOMBRE=$(echo "$USER_INFO" | jq -r '.nombre' 2>/dev/null)
        if [ -n "$NOMBRE" ] && [ "$NOMBRE" != "null" ]; then
            echo -e "   ${GREEN}✅ Usuario autenticado: $NOMBRE${NC}"
        fi
    else
        echo -e "   ${RED}❌ Login falló${NC}"
    fi
    
    echo ""
    
    # 4. Verificar datos
    echo "📊 Datos disponibles en el sistema:"
    CHILDREN_COUNT=$(curl -s http://localhost:8000/api/children/ 2>/dev/null | jq '. | length' 2>/dev/null)
    SEDES_COUNT=$(curl -s http://localhost:8000/api/sedes/ 2>/dev/null | jq '. | length' 2>/dev/null)
    ACUDIENTES_COUNT=$(curl -s http://localhost:8000/api/acudientes/ 2>/dev/null | jq '. | length' 2>/dev/null)
    
    [ -n "$CHILDREN_COUNT" ] && echo "   - Niños: $CHILDREN_COUNT"
    [ -n "$SEDES_COUNT" ] && echo "   - Sedes: $SEDES_COUNT"
    [ -n "$ACUDIENTES_COUNT" ] && echo "   - Acudientes: $ACUDIENTES_COUNT"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Resumen final
if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ]; then
    echo -e "${GREEN}🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!${NC}"
    echo ""
    echo "📱 Acceder a la aplicación:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔑 Credenciales de administrador:"
    echo "   Email:    admin@example.com"
    echo "   Password: admin123"
    echo ""
else
    echo -e "${RED}❌ ALGUNOS SERVICIOS FALLARON${NC}"
    echo ""
    echo "📋 Comandos útiles para diagnosticar:"
    echo "   Ver logs: docker-compose logs -f"
    echo "   Estado:   docker-compose ps"
    echo "   Reiniciar: docker-compose restart"
fi

echo ""
