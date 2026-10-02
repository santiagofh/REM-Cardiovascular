# Lanzador del dashboard cardiovascular vigente.
# Uso: clic derecho > Ejecutar con PowerShell, o desde terminal:
#   .\run_dashboard.ps1 [-Port 8501]
# El dashboard vigente es streamlit_dashboard.py (raíz) con datos de 2025/.
# La carpeta D/ es legacy congelada (ver D/LEEME_LEGACY.md): no lanzar sus dashboards.
param(
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$dashboard = Join-Path $PSScriptRoot "streamlit_dashboard.py"
if (-not (Test-Path -LiteralPath $dashboard)) {
    throw "No se encontró $dashboard"
}

& py -m streamlit run $dashboard --server.port $Port
