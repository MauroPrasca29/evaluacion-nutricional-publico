#!/bin/bash

# Script de prueba para verificar la integración de anemia
# Verifica que el servicio esté respondiendo correctamente

echo "========================================="
echo "Prueba de Integración - Detección de Anemia"
echo "========================================="
echo ""

# Variables
BACKEND_URL="http://localhost:8000"
ANEMIA_SERVICE_URL="http://localhost:8001"
TEST_IMAGE_PATH="./public/anemia_test_image.jpg"

echo "1. Verificando conectividad..."
echo "   - Backend: $BACKEND_URL/health"

curl -s "$BACKEND_URL/health" | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "   ✅ Backend OK"
else
    echo "   ❌ Backend no responde"
    exit 1
fi

echo "   - Anemia Service: $ANEMIA_SERVICE_URL/health"
curl -s "$ANEMIA_SERVICE_URL/health" | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "   ✅ Anemia Service OK"
else
    echo "   ❌ Anemia Service no responde"
    exit 1
fi

echo ""
echo "2. Probando endpoint de predicción..."
echo "   POST $BACKEND_URL/api/vision/predict-anemia"
echo ""

# Nota: Para una prueba real necesitarías una imagen válida
echo "   ⚠️  Para una prueba completa, necesitas una imagen de ojo válida"
echo "   📝 Uso:"
echo "      curl -F 'file=@/ruta/a/imagen.jpg' \\"
echo "           -F 'age_months=24' \\"
echo "           http://localhost:8000/api/vision/predict-anemia"

echo ""
echo "3. Verificando estructura..."
echo ""

# Verificar que los archivos estén en su lugar
echo "   Archivos requeridos:"
FILES=(
    "components/NewFollowUpForm.tsx"
    "components/FollowUpResults.tsx"
    "backend/src/api/vision.py"
    "backend/main.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (FALTA)"
    fi
done

echo ""
echo "========================================="
echo "Prueba completada"
echo "========================================="
echo ""
echo "Para una prueba manual del formulario:"
echo "1. Accede a http://localhost:3000"
echo "2. Crea un nuevo seguimiento"
echo "3. Sube una foto clara de los ojos"
echo "4. Verifica el análisis en tiempo real"
