$baseUrl = "https://repositoriodeis.minsal.cl/DatosAbiertos/EGRESOS"
$destino = "C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular\D"
$anioInicio = 2020
$anioLimite = (Get-Date).Year + 2
$erroresConsecutivos = 0

Add-Type -AssemblyName System.IO.Compression.FileSystem

if (-not (Test-Path $destino)) {
    New-Item -ItemType Directory -Path $destino -Force | Out-Null
}

for ($anio = $anioInicio; $anio -le $anioLimite; $anio++) {
    $url = "$baseUrl/EGRESOS_$anio.zip"
    $zipPath = Join-Path $destino "EGRESOS_$anio.zip"
    $extractDir = Join-Path $destino "EGRESOS_$anio"

    try {
        $resp = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -ErrorAction Stop
        $serverModified = [DateTime]::Parse($resp.Headers.'Last-Modified'[0])
        $serverSize = [long]$resp.Headers.'Content-Length'[0]
        $erroresConsecutivos = 0
    }
    catch {
        Write-Host "EGRESOS_$anio.zip no disponible en el servidor" -ForegroundColor Yellow
        $erroresConsecutivos++
        if ($erroresConsecutivos -ge 2) {
            Write-Host "No hay más años disponibles. Deteniendo..." -ForegroundColor Magenta
            break
        }
        continue
    }

    $debeDescargar = $false
    if (-not (Test-Path $zipPath)) {
        $debeDescargar = $true
        $razon = "no existe localmente"
    }
    else {
        $localModified = (Get-Item $zipPath).LastWriteTime
        $localSize = (Get-Item $zipPath).Length
        if ($serverModified -gt $localModified) {
            $debeDescargar = $true
            $razon = "servidor tiene versión más reciente (servidor: $($serverModified.ToString('yyyy-MM-dd HH:mm')), local: $($localModified.ToString('yyyy-MM-dd HH:mm')))"
        }
        elseif ($serverSize -ne $localSize) {
            $debeDescargar = $true
            $razon = "tamaño diferente (servidor: $serverSize, local: $localSize)"
        }
        else {
            Write-Host "EGRESOS_$anio.zip actualizado ($($localModified.ToString('yyyy-MM-dd HH:mm')))" -ForegroundColor Yellow
        }
    }

    if ($debeDescargar) {
        Write-Host "Descargando EGRESOS_$anio.zip ($razon)..." -ForegroundColor Green
        try {
            Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
            (Get-Item $zipPath).LastWriteTime = $serverModified
            Write-Host "  Descargado correctamente" -ForegroundColor Cyan
        }
        catch {
            Write-Host "  Error en descarga: $_" -ForegroundColor Red
            continue
        }
    }

    if (Test-Path $extractDir) {
        $dirModified = (Get-Item $extractDir).LastWriteTime
        if ($serverModified -gt $dirModified) {
            Write-Host "  Servidor más reciente, re-descomprimiendo..." -ForegroundColor Green
            Remove-Item $extractDir -Recurse -Force
        }
        else {
            Write-Host "  Ya descomprimido" -ForegroundColor Yellow
            continue
        }
    }

    Write-Host "  Descomprimiendo..." -ForegroundColor Green
    try {
        [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $extractDir)
        (Get-Item $extractDir).LastWriteTime = $serverModified
        Write-Host "  Descomprimido en $extractDir" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  Error descomprimiendo: $_" -ForegroundColor Red
    }
}

Write-Host "`nProceso completado." -ForegroundColor Green
Write-Host "`nResumen:" -ForegroundColor Cyan
Get-ChildItem $destino -Directory | Sort-Object Name | ForEach-Object {
    $zip = Get-Item (Join-Path $destino "$($_.Name).zip") -ErrorAction SilentlyContinue
    $files = (Get-ChildItem $_.FullName -File).Count
    $modified = if ($zip) { $zip.LastWriteTime.ToString('yyyy-MM-dd HH:mm') } else { 'N/A' }
    Write-Host "  $($_.Name)  |  ZIP: $modified  |  $files archivos"
}
