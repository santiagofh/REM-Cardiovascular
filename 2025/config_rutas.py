"""Rutas centrales del pipeline cardiovascular.

Todos los scripts de `2025/` deben importar desde aquí en vez de hardcodear
rutas absolutas. Cada ruta acepta override por variable de entorno, de modo que
el pipeline corre en otra máquina sin editar código. Ejemplo (PowerShell):

    $env:CARDIO_REPO_ROOT = "E:\\respaldos\\REM-Cardiovascular"
    py calcular_indicadores_cardiovascular_2024_2025.py

Variables disponibles: CARDIO_REPO_ROOT, CARDIO_MASTER_ESTABLECIMIENTOS,
CARDIO_SERIE_P_2024, CARDIO_SERIE_P_2025, CARDIO_DICCIONARIO_SP_2025,
CARDIO_FONASA_INSCRITOS_2023/2024/2025, CARDIO_BENEFICIARIOS_DIR,
CARDIO_EGRESOS_DIR.
"""

from __future__ import annotations

import os
from pathlib import Path


def _ruta(nombre_env: str, valor_por_defecto: str) -> Path:
    return Path(os.environ.get(nombre_env, valor_por_defecto))


# Raíz del producto (este repo).
REPO_ROOT = _ruta(
    "CARDIO_REPO_ROOT",
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular",
)
DATA_DIR = REPO_ROOT / "2025"

# Planilla oficial de indicadores (raíz del repo).
PLANILLA_INDICADORES = (
    REPO_ROOT / "Planilla indicadores y fechas reuniones macrozonales 2026.xlsx"
)

# Maestro de establecimientos DEIS.
MASTER_ESTABLECIMIENTOS = _ruta(
    "CARDIO_MASTER_ESTABLECIMIENTOS",
    r"D:\DATA\ESTABLECIMIENTOS\establecimientos_20260730.csv",
)

# Series REM P por año.
SERIE_P = {
    2024: _ruta(
        "CARDIO_SERIE_P_2024",
        r"D:\DATA\REM\REM_2024\Datos\SerieP2024.csv",
    ),
    2025: _ruta(
        "CARDIO_SERIE_P_2025",
        r"D:\DATA\REM\REM_2025\Datos\SerieP2025.csv",
    ),
}

# Diccionario oficial REM Serie P.
DICCIONARIO_SP_2025 = _ruta(
    "CARDIO_DICCIONARIO_SP_2025",
    r"D:\DATA\REM\REM_2025\Diccionarios\DICCIONARIO CODIGOS SP_25_V1.2.xlsm",
)

# Inscritos FONASA por año de indicador (base de pago siguiente).
FONASA_INSCRITOS = {
    2023: _ruta(
        "CARDIO_FONASA_INSCRITOS_2023",
        r"D:\DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2022 (Base pago 2023)\T5385_Poblacion_Inscrita_RM.xlsx",
    ),
    2024: _ruta(
        "CARDIO_FONASA_INSCRITOS_2024",
        r"D:\DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2023 (Base pago 2024)\Copia de T6603_Inscritos.xlsx",
    ),
    2025: _ruta(
        "CARDIO_FONASA_INSCRITOS_2025",
        r"D:\DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2024 (Base pago 2025)\T8009_Inscritos_RM.xlsx",
    ),
}

# Beneficiarios FONASA (SEREMI Estadísticas).
BENEFICIARIOS_DIR = _ruta(
    "CARDIO_BENEFICIARIOS_DIR",
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\SEREMIRM - Estadistica\A Estadisticas Sanitarias y Demograficas\POBLACIONES\BENEFICIARIOS\Datos FONASA",
)

# Egresos hospitalarios DEIS (datos abiertos).
EGRESOS_DIR = _ruta(
    "CARDIO_EGRESOS_DIR",
    "D:/DATA/EGRESOS_HOSPITALARIOS_C",
)

CSV_ENCODING = "utf-8-sig"
