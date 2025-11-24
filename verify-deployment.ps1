param(
    [switch]$Verbose,
    [switch]$RunTests
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "===================================================="
Write-Host "VERIFICACION PRE-DEPLOY - Sistema de Evaluacion Nutricional"
Write-Host "===================================================="
Write-Host ""

$allChecksPassed = $true
$checksResults = @()

# ==================== FUNCIONES ====================
function Test-Service {
    param(
        [string]$Name,
        [string]$Url,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )
    
    Write-Host -NoNewline "[*] Verificando $Name... "
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 401) {
                Write-Host "[OK]"
                return $true
            }
        }
        catch {
            if ($i -eq $MaxAttempts) {
                Write-Host "[FALLO - No responde]"
                return $false
            }
            Start-Sleep -Seconds $DelaySeconds
        }
    }
    
    Write-Host "[FALLO]"
    return $false
}

# ==================== 1. VERIFICAR DOCKER ====================
Write-Host "[1/7] Verificando Docker"
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "[OK] Docker instalado: $dockerVersion"
    $checksResults += @{ Check = "Docker"; Status = "OK" }
}
catch {
    Write-Host "[ERROR] Docker NO esta instalado o accesible"
    $checksResults += @{ Check = "Docker"; Status = "FALLO" }
    $allChecksPassed = $false
}

# ==================== 2. VERIFICAR DOCKER COMPOSE ====================
Write-Host ""
Write-Host "[2/7] Verificando Docker Compose"
try {
    $composeVersion = docker-compose --version 2>$null
    Write-Host "[OK] Docker Compose instalado: $composeVersion"
    $checksResults += @{ Check = "Docker Compose"; Status = "OK" }
}
catch {
    Write-Host "[ERROR] Docker Compose NO esta instalado o accesible"
    $checksResults += @{ Check = "Docker Compose"; Status = "FALLO" }
    $allChecksPassed = $false
}

# ==================== 3. VERIFICAR CONTENEDORES ====================
Write-Host ""
Write-Host "[3/7] Verificando Contenedores Activos"
try {
    $ps = docker ps 2>$null
    if ($null -ne $ps) {
        Write-Host "[OK] Docker daemon accesible"
        $checksResults += @{ Check = "Contenedores"; Status = "OK" }
    }
}
catch {
    Write-Host "[ERROR] No se puede acceder a Docker daemon"
    $checksResults += @{ Check = "Contenedores"; Status = "ERROR" }
}

# ==================== 4. VERIFICAR BACKEND ====================
Write-Host ""
Write-Host "[4/7] Verificando Backend (FastAPI)"
$backendOk = Test-Service -Name "Backend" -Url "http://localhost:8000/health"
if ($backendOk) {
    $checksResults += @{ Check = "Backend API"; Status = "OK" }
    
    try {
        $docs = Invoke-WebRequest -Uri "http://localhost:8000/docs" -ErrorAction Stop
        Write-Host "[OK] Documentacion API disponible: http://localhost:8000/docs"
    }
    catch {
        Write-Host "[ADVERTENCIA] Documentacion API NO disponible"
    }
}
else {
    $checksResults += @{ Check = "Backend API"; Status = "FALLO" }
    $allChecksPassed = $false
}

# ==================== 5. VERIFICAR FRONTEND ====================
Write-Host ""
Write-Host "[5/7] Verificando Frontend (Next.js)"
$frontendOk = Test-Service -Name "Frontend" -Url "http://localhost:3000"
if ($frontendOk) {
    Write-Host "[OK] Frontend disponible: http://localhost:3000"
    $checksResults += @{ Check = "Frontend"; Status = "OK" }
}
else {
    $checksResults += @{ Check = "Frontend"; Status = "FALLO" }
    $allChecksPassed = $false
}

# ==================== 6. VERIFICAR AUTENTICACION ====================
Write-Host ""
Write-Host "[6/7] Verificando Autenticacion"
if ($backendOk) {
    try {
        $loginBody = @{
            correo = "admin@example.com"
            contrasena = "admin123"
        } | ConvertTo-Json
        
        $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
            -Method POST `
            -ContentType "application/json" `
            -Body $loginBody `
            -ErrorAction Stop
        
        $loginData = $loginResponse.Content | ConvertFrom-Json
        $token = $loginData.access_token
        
        if ($token) {
            Write-Host "[OK] Login funcionando correctamente"
            
            try {
                $userInfo = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/me" `
                    -Headers @{ Authorization = "Bearer $token" } `
                    -ErrorAction Stop | ConvertFrom-Json
                
                Write-Host "[OK] Usuario autenticado: $($userInfo.nombre)"
                $checksResults += @{ Check = "Autenticacion"; Status = "OK" }
            }
            catch {
                Write-Host "[ERROR] No se pudo obtener informacion del usuario"
                $checksResults += @{ Check = "Autenticacion"; Status = "FALLO" }
                $allChecksPassed = $false
            }
        }
        else {
            Write-Host "[ERROR] No se obtuvo token de autenticacion"
            $checksResults += @{ Check = "Autenticacion"; Status = "FALLO" }
            $allChecksPassed = $false
        }
    }
    catch {
        Write-Host "[ERROR] Error en autenticacion: $($_.Exception.Message)"
        $checksResults += @{ Check = "Autenticacion"; Status = "FALLO" }
        $allChecksPassed = $false
    }
}
else {
    Write-Host "[SKIP] No se puede verificar autenticacion (Backend no disponible)"
    $checksResults += @{ Check = "Autenticacion"; Status = "SKIP" }
}

# ==================== 7. VERIFICAR BASE DE DATOS ====================
Write-Host ""
Write-Host "[7/7] Verificando Base de Datos"
if ($backendOk) {
    try {
        $childrenResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/children/" `
            -ErrorAction Stop | ConvertFrom-Json
        
        $childrenCount = $childrenResponse.Count
        Write-Host "[OK] Base de datos accesible"
        Write-Host "     - Ninos registrados: $childrenCount"
        
        $checksResults += @{ Check = "Base de Datos"; Status = "OK" }
    }
    catch {
        Write-Host "[ERROR] Error al acceder a base de datos: $($_.Exception.Message)"
        $checksResults += @{ Check = "Base de Datos"; Status = "FALLO" }
        $allChecksPassed = $false
    }
}
else {
    Write-Host "[SKIP] No se puede verificar BD (Backend no disponible)"
    $checksResults += @{ Check = "Base de Datos"; Status = "SKIP" }
}

# ==================== RESUMEN ====================
Write-Host ""
Write-Host "===================================================="
Write-Host "RESUMEN DE VERIFICACIONES"
Write-Host "===================================================="
Write-Host ""

foreach ($result in $checksResults) {
    $checkName = $result.Check
    $checkStatus = $result.Status
    
    if ($checkStatus -eq "OK") {
        Write-Host "[OK] $checkName : $checkStatus"
    }
    elseif ($checkStatus -eq "SKIP") {
        Write-Host "[*] $checkName : $checkStatus"
    }
    else {
        Write-Host "[ERROR] $checkName : $checkStatus"
    }
}

Write-Host ""
Write-Host "===================================================="
Write-Host ""

if ($allChecksPassed) {
    Write-Host "EXITO - SISTEMA COMPLETAMENTE FUNCIONAL!"
    Write-Host ""
    Write-Host "Puedes acceder a la aplicacion en:"
    Write-Host "   Frontend: http://localhost:3000"
    Write-Host "   Backend:  http://localhost:8000"
    Write-Host "   Docs API: http://localhost:8000/docs"
    Write-Host ""
    Write-Host "LISTO PARA DEPLOY"
    Write-Host ""
    exit 0
}
else {
    Write-Host "ADVERTENCIA - Existen problemas que deben resolverse antes del deploy"
    Write-Host ""
    Write-Host "Acciones recomendadas:"
    Write-Host "1. Ejecuta: docker-compose up -d"
    Write-Host "2. Espera a que los contenedores se estabilicen (2-3 minutos)"
    Write-Host "3. Vuelve a ejecutar este script"
    Write-Host ""
    exit 1
}
