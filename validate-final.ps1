$PASSED = 0
$FAILED = 0

function Check-Result {
    param([bool]$Success, [string]$Message)
    if ($Success) {
        Write-Host "[OK] $Message" -ForegroundColor Green
        $global:PASSED++
    } else {
        Write-Host "[FAIL] $Message" -ForegroundColor Red
        $global:FAILED++
    }
}

Write-Host ""
Write-Host "==== VALIDACION FINAL DEL SISTEMA ====" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar archivos clave
Write-Host "1. Verificando archivos..." -ForegroundColor Yellow
Check-Result (Test-Path "components/NewFollowUpForm.tsx") "NewFollowUpForm.tsx existe"
Check-Result (Test-Path "components/FollowUpResults.tsx") "FollowUpResults.tsx existe"
Check-Result (Test-Path "backend/src/api/vision.py") "backend/src/api/vision.py existe"
Check-Result (Test-Path "backend/main.py") "backend/main.py existe"
Check-Result (Test-Path "docker-compose.yml") "docker-compose.yml existe"
Check-Result (Test-Path "anemia-service/main.py") "anemia-service/main.py existe"
Check-Result (Test-Path "anemia-service/requirements.txt") "anemia-service/requirements.txt existe"

Write-Host ""
Write-Host "2. Verificando integracion de anemia..." -ForegroundColor Yellow

$formContent = Get-Content "components/NewFollowUpForm.tsx" -Raw
Check-Result ($formContent -like "*predictAnemiaFromImage*") "NewFollowUpForm tiene metodo predictAnemiaFromImage"
Check-Result ($formContent -like "*anemiaResult*") "NewFollowUpForm maneja estado de anemia"

$resultsContent = Get-Content "components/FollowUpResults.tsx" -Raw
Check-Result ($resultsContent -like '*value="anemia"*') "FollowUpResults tiene tab de anemia"
Check-Result ($resultsContent -like "*grid-cols-4*") "FollowUpResults tiene 4 columnas de tabs"

Write-Host ""
Write-Host "3. Verificando endpoint vision..." -ForegroundColor Yellow

$visionContent = Get-Content "backend/src/api/vision.py" -Raw
Check-Result ($visionContent -like "*predict_anemia*") "vision.py tiene endpoint"
Check-Result ($visionContent -like "*hb_estimate*") "vision.py calcula hemoglobina"

$mainContent = Get-Content "backend/main.py" -Raw
Check-Result ($mainContent -like "*vision_router*") "backend/main.py registra vision_router"

Write-Host ""
Write-Host "4. Verificando docker-compose..." -ForegroundColor Yellow

$dockerContent = Get-Content "docker-compose.yml" -Raw
Check-Result ($dockerContent -like "*anemia-service*") "docker-compose define anemia-service"
Check-Result ($dockerContent -like "*8001:8000*") "puerto 8001 mapeado correctamente"

Write-Host ""
Write-Host "5. Verificando servicios docker..." -ForegroundColor Yellow

$containers = docker-compose ps 2>$null
Check-Result ($containers -like "*frontend*") "frontend registrado"
Check-Result ($containers -like "*backend*") "backend registrado"
Check-Result ($containers -like "*anemia-service*") "anemia-service registrado"
Check-Result ($containers -like "*db*") "db registrado"

Write-Host ""
Write-Host "6. Verificando health checks..." -ForegroundColor Yellow

try {
    $healthResp = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    $isHealthy = $healthResp.Content -like "*healthy*"
    Check-Result $isHealthy "Backend /health responde"
} catch {
    Check-Result $false "Backend /health responde"
}

try {
    $anemiaResp = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    $isHealthy = $anemiaResp.Content -like "*healthy*"
    Check-Result $isHealthy "Anemia-service /health responde"
} catch {
    Check-Result $false "Anemia-service /health responde"
}

Write-Host ""
Write-Host "7. Verificando documentacion..." -ForegroundColor Yellow

Check-Result (Test-Path "INTEGRACION_ANEMIA.md") "INTEGRACION_ANEMIA.md existe"
Check-Result (Test-Path "RESUMEN_INTEGRACION.md") "RESUMEN_INTEGRACION.md existe"
Check-Result (Test-Path "QUICK_REFERENCE_ANEMIA.md") "QUICK_REFERENCE_ANEMIA.md existe"
Check-Result (Test-Path "VALIDACION_INTEGRACION.md") "VALIDACION_INTEGRACION.md existe"

Write-Host ""
Write-Host "=== RESULTADO ===" -ForegroundColor Cyan

$TOTAL = $PASSED + $FAILED
$PCT = if ($TOTAL -gt 0) { [math]::Round(($PASSED * 100) / $TOTAL) } else { 0 }

Write-Host "Total: $TOTAL | Exitosos: $PASSED | Fallidos: $FAILED" -ForegroundColor Cyan
Write-Host "Exito: $PCT%" -ForegroundColor Cyan

if ($FAILED -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS - Sistema listo para commit" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "FAILED - Revisar errores antes de commit" -ForegroundColor Red
    Write-Host ""
}
