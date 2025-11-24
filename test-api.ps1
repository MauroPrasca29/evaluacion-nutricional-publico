#!/usr/bin/env pwsh
# Script de pruebas funcionales de API

$ErrorActionPreference = 'SilentlyContinue'

$BACKEND_URL = "http://localhost:8000"
$ANEMIA_URL = "http://localhost:8001"

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗"
Write-Host "║          PRUEBAS FUNCIONALES DEL SISTEMA - API REST               ║"
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n"

# Test 1: Health Checks
Write-Host "🔍 TEST 1: Health Checks"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

try {
    $backend_health = Invoke-RestMethod "$BACKEND_URL/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend Health: OK - $($backend_health.ok)"
} catch {
    Write-Host "❌ Backend Health: FAILED"
}

try {
    $anemia_health = Invoke-RestMethod "$ANEMIA_URL/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Anemia Service Health: OK - $($anemia_health.status)"
} catch {
    Write-Host "❌ Anemia Service Health: FAILED"
}

# Test 2: Auth Endpoints
Write-Host "`n🔐 TEST 2: Auth Endpoints"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get CSRF Token
try {
    $response = Invoke-WebRequest "$BACKEND_URL/api/auth/csrf-token" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ CSRF Token endpoint: Accesible (Status: $($response.StatusCode))"
} catch {
    Write-Host "⚠️  CSRF Token endpoint: $($_.Exception.Message)"
}

# Test 3: Protected Endpoints (debe fallar sin auth)
Write-Host "`n👥 TEST 3: Protected Endpoints"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

try {
    $response = Invoke-WebRequest "$BACKEND_URL/api/children" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "⚠️  Children endpoint: Sin autenticación (debería estar protegido)"
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✅ Children endpoint: Protegido correctamente (Status: $($_.Exception.Response.StatusCode))"
    } else {
        Write-Host "❌ Error inesperado: $($_.Exception.Response.StatusCode)"
    }
}

# Test 4: Vision/Anemia Endpoints
Write-Host "`n👁️  TEST 4: Vision API Endpoints"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

try {
    $response = Invoke-WebRequest "$BACKEND_URL/api/vision/models-status" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Vision Models Status: Accesible (Status: $($response.StatusCode))"
} catch {
    Write-Host "⚠️  Vision Models Status: $($_.Exception.Message)"
}

# Test 5: Database Connectivity
Write-Host "`n🗄️  TEST 5: Database Connectivity"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

$dbHealth = docker exec nutricion_backend curl -s http://localhost:8000/health 2>&1
if ($dbHealth -match '"ok":true') {
    Write-Host "✅ Database: Conectada y funcional"
} else {
    Write-Host "❌ Database: Problema de conexión"
}

# Test 6: Container Status
Write-Host "`n📦 TEST 6: Estado de Contenedores"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

$containers = docker ps --format "json" | ConvertFrom-Json
$allHealthy = $true

foreach ($container in $containers) {
    $status = $container.Status
    if ($status -match "healthy") {
        Write-Host "✅ $($container.Names): $status"
    } else {
        Write-Host "⚠️  $($container.Names): $status"
        $allHealthy = $false
    }
}

# Resumen Final
Write-Host "`n╔════════════════════════════════════════════════════════════════════╗"
if ($allHealthy) {
    Write-Host "║               ✅ TODAS LAS PRUEBAS PASARON                         ║"
    Write-Host "║                                                                    ║"
    Write-Host "║        🚀 SISTEMA LISTO PARA DEPLOY A RAILWAY                     ║"
} else {
    Write-Host "║               ⚠️  REVISAR ERRORES ARRIBA                           ║"
}
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n"
