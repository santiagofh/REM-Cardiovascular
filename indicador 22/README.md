# Indicador 22

Esta carpeta reúne una propuesta paralela para investigar cómo aproximar o reproducir el indicador 22 oficial:

- Indicador: `Tasa de egresos hospitalarios en personas con diabetes mellitus y amputación del pie diabético`
- Fuente oficial declarada: `Tablero PSCV DEIS + población beneficiaria FONASA`

## Hallazgos principales

- El cálculo local previo del proyecto no replica la definición oficial.
- El denominador local usado en el dashboard (`4.632.711` en 2024) corresponde a `población inscrita validada 15+`.
- La planilla oficial 2024 usa un denominador distinto: `5.108.594`, rotulado como `población beneficiaria FONASA 15+`.
- El numerador local previo del proyecto (`166` en 2024 RM) sale de una regla demasiado restrictiva y no es comparable con el oficial `3.936`.

## Pistas útiles encontradas

- En `EH_2024.csv` sí existen más campos de procedimiento/intervención que los que usaba el script productivo:
  - `INTERV_Q`, `INTERV_Q_PPAL`, `INTERV_Q_2`, `INTERV_Q_3`
  - `PROCED`, `PROCED_PPAL`, `PROCED_2`, `PROCED_3`
- Solo usar `DIAG1` de diabetes y `PROCED_PPAL` que empieza en `1701` deja el numerador muy abajo.
- Variantes más amplias sobre diagnósticos de diabetes en cualquier posición y familias de intervención/procedimiento cercanas a amputación acercan el conteo al orden de magnitud oficial, pero no lo reproducen exactamente.

## Script

- `explorar_indicador_22.py`

Este script:

- estima el denominador `15+` desde la planilla de beneficiarios 2024
- prueba varias reglas de numerador sobre egresos 2024
- entrega un resumen para comparar escenarios

## Recomendación

Si se necesita reproducir exactamente el valor oficial, lo más probable es que haya que:

1. confirmar la regla exacta del denominador `beneficiarios FONASA 15+`
2. confirmar la codificación exacta de amputación usada por el tablero PSCV DEIS
3. validar si el tablero usa una combinación de `INTERV_Q*` y/o `PROCED*`, y no solo el procedimiento principal
