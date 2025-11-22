#!/bin/bash
# Script para desplegar y verificar el servicio de anemia

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 DESPLIEGUE DEL SERVICIO DE ANEMIA                     ║"
echo "║     Modelo ONNX desde Hugging Face                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Verificar Docker
echo "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi
print_status "Docker disponible"

# Verificar Docker Compose
echo "Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    exit 1
fi
print_status "Docker Compose disponible"

# Construcción
echo ""
echo "Construyendo imágenes Docker..."
docker-compose build --no-cache anemia-service || {
    print_error "Error en la construcción"
    exit 1
}
print_status "Construcción completada"

# Despliegue
echo ""
echo "Iniciando servicios..."
docker-compose up -d db backend anemia-service || {
    print_error "Error al iniciar servicios"
    exit 1
}
print_status "Servicios iniciados"

# Esperar a que esté listo
echo ""
echo "Esperando a que los servicios estén listos..."
sleep 10

# Verificar salud
echo ""
echo "Verificando salud de servicios..."

# Base de datos
if docker-compose exec -T db pg_isready -U postgres &> /dev/null; then
    print_status "Base de datos: ✓ Saludable"
else
    print_info "Base de datos: Iniciando..."
fi

# Backend
if curl -s http://localhost:8000/health &> /dev/null; then
    print_status "Backend: ✓ Saludable (puerto 8000)"
else
    print_info "Backend: Iniciando..."
fi

# Anemia Service
if curl -s http://localhost:8001/health &> /dev/null; then
    print_status "Anemia Service: ✓ Saludable (puerto 8001)"
else
    print_info "Anemia Service: Iniciando (puede tomar más tiempo)..."
    echo "Esperando descarga del modelo desde Hugging Face..."
    sleep 30
    
    if curl -s http://localhost:8001/health &> /dev/null; then
        print_status "Anemia Service: ✓ Saludable (puerto 8001)"
    else
        print_error "Anemia Service no responde"
        echo "Ver logs: docker-compose logs anemia-service"
        exit 1
    fi
fi

# Información de acceso
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ DESPLIEGUE COMPLETADO                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Servicios disponibles:"
echo "   • Frontend:       http://localhost:3000"
echo "   • Backend:        http://localhost:8000"
echo "   • Anemia Service: http://localhost:8001"
echo ""
echo "🔗 URLs útiles:"
echo "   • API Docs:       http://localhost:8001/docs"
echo "   • Health:         http://localhost:8001/health"
echo ""
echo "📊 Comandos útiles:"
echo "   • Ver logs:       docker-compose logs -f anemia-service"
echo "   • Parar:          docker-compose down"
echo "   • Ejecutar tests: docker-compose run --rm test"
echo ""
echo "🧪 Prueba rápida con cURL:"
echo ""
echo '   curl -X POST "http://localhost:8001/predict" \\'
echo '     -F "file=@imagen.jpg" \\'
echo '     -F "age_months=24"'
echo ""
