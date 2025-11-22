#!/bin/bash
# Script de verificacion rapida post-deploy
# Ejecutar despues de: docker-compose up -d

echo "====== VERIFICACION POST-DEPLOY ======"
echo ""

# Esperar a que los servicios inicien
echo "Esperando a que los servicios inicien..."
sleep 10

echo ""
echo "1. Estado de contenedores:"
docker-compose ps | grep -E "up|down" | awk '{print $1, $2}'

echo ""
echo "2. Test de conectividad Backend:"
curl -s http://localhost:8000/health | head -c 100
echo ""

echo ""
echo "3. Test de conectividad Anemia Service:"
curl -s http://localhost:8001/health | head -c 100
echo ""

echo ""
echo "4. Listando datos de base de datos:"
curl -s http://localhost:8000/api/children | python3 -m json.tool 2>/dev/null | head -20

echo ""
echo "====== VERIFICACION COMPLETA ======"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "Anemia:   http://localhost:8001"
