# D/ — PIPELINE LEGACY (congelado 2026-10-02)

No ejecutar los scripts de esta carpeta. El pipeline vigente vive en `../2025/`
y el dashboard vigente en la raíz (`../streamlit_dashboard.py` +
`../dashboard_cardiovascular_pages.py`, que leen `../2025/*.csv`).

## Por qué se congeló

- `calcular_indicadores_cardiovasculares.py` usa solo `Mes == 12`, denominador
  2024 con FONASA 2025, ignora el numerador A05 que extrae, y suma tasas en el
  dashboard (`tasa_x10000:sum`).
- `calcular_indicadores_egresos.py` usa denominador fijo 5.108.594 para
  2020-2024 y solo mira `DIAG1` (el pipeline `2025/` mira DIAG1-11 +
  procedimientos y usa denominador FONASA por año).
- Los dashboards `D/` están 2-3 días desactualizados respecto a los de la raíz
  y apuntaban a `D/output/`, que se movió a `históricos/`.

## Qué se movió a `históricos/`

- `output_legacy_2026-10-02/` (71 CSV generados por el pipeline legacy).
- `EGRESOS_2020.zip` … `EGRESOS_2024.zip` (descargables de nuevo con
  `descargar_egresos.ps1`).

## Qué se dejó en su lugar

- `EGRESOS_2020/` … `EGRESOS_2024/` (1,3 GB ya extraídos; se dejan para no
  mover peso innecesario; son re-descargables).
- Scripts, JSON y `factibilidad_indicadores.md` como referencia histórica.
- `assets/` (logos que también usa el dashboard vigente: no tocar).
