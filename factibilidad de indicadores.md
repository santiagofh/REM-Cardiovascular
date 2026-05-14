# Factibilidad de Indicadores REM-Cardiovascular

Este documento **ignora la carpeta `D`** y se basa solo en la información actualmente disponible en `REM-Cardiovascular` y en las bases locales que ya usan los otros proyectos REM.

## Insumos locales disponibles hoy

- **REM Serie P cruda disponible:** `2024` y `2025`
  - `C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2024\Datos\SerieP2024.csv`
  - `C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM\REM_2025\Datos\SerieP2025.csv`
- **Diccionarios P4 disponibles:** `2024` y `2025`
- **Población inscrita y validada FONASA disponible localmente:**
  - `Inscritos 2022 (Base pago 2023)` -> usable como denominador para año indicador `2023`
  - `Inscritos 2023 (Base pago 2024)` -> usable como denominador para año indicador `2024`
  - `Inscritos 2024 (Base pago 2025)` -> usable como denominador para año indicador `2025`
- **Maestro de establecimientos disponible y homologado:** `establecimientos_20260424.csv`
- **Egresos hospitalarios abiertos disponibles localmente:** `2020`, `2021`, `2022`, `2023`, `2024`
  - Ruta base: `D:\DATA\EGRESOS_HOSPITALARIOS`
  - Variables utilizables: pertenencia SNSS/no SNSS, grupo etario, previsión, región de residencia, diagnóstico principal `DIAG1`
  - Limitación: en `2023` y `2024` ya no vienen campos de procedimiento/intervención.

## Archivos generados en esta etapa

- `C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular\2025\poblacion_inscrita_validada_15_mas_rm_establecimiento_2023_2025.csv`
- `C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular\2025\poblacion_inscrita_validada_15_mas_rm_resumen_anual_2023_2025.csv`
- `C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular\2025\diccionario_poblacion_inscrita_validada_15_mas_rm_2023_2025.json`
- `C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular\2025\egresos_hospitalarios_factibilidad_resumen_2020_2024.csv`

## Resumen rápido

- **Con exactitud en 2025:** `1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12b, 13, 14, 15, 16, 17`
- **Con exactitud en 2024:** `1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12b, 13, 14`
- **Parcial / no exacto:** `12a`
- **Viables con datos de egresos hasta 2024:** `18, 19, 20, 21`
- **No factible hoy con datos locales:** `5, 22` y cualquier versión `2025` de `18-22`

## Factibilidad por indicador

| Indicador | 2024 | 2025 | Estado actual | Observación |
|---|---|---|---|---|
| 1. Cobertura de HTA | Sí | Sí | Exacto | Numerador `P4150601`; denominador = población inscrita validada 15+ x `27,6%`. |
| 2. Control de HTA | Sí | Sí | Exacto | Numerador `P4180200 + P4200100`; denominador `P4150601`. |
| 3. Cobertura efectiva de HTA | Sí | Sí | Exacto | Mismo numerador del indicador 2; denominador = población inscrita validada 15+ x `27,6%`. |
| 4. HTA muy descompensadas | Sí | Sí | Exacto | Numerador `P4200400`; denominador `P4150601`. |
| 5. Índice de Madurez HEARTS | No | No | No factible local | La planilla dice "fuente de información respectiva". El `P4302103 Protocolo HEARTS` no reemplaza el índice de madurez. |
| 6. Cobertura de DM2 | Sí | Sí | Exacto | Numerador `P4150602`; denominador = población inscrita validada 15+ x `12,3%`. |
| 7. Control de DM2 | Sí | Sí | Exacto | Numerador `P4180300 + P4200200`; denominador `P4150602`. |
| 8. Cobertura efectiva de DM2 | Sí | Sí | Exacto | Mismo numerador del indicador 7; denominador = población inscrita validada 15+ x `12,3%`. |
| 9. DM2 muy descompensadas | Sí | Sí | Exacto | Numerador `P4190960`; denominador `P4150602`. |
| 10. DM2 compensada usuarias de insulina | Sí | Sí | Exacto | Numerador `P4200700`; denominador `P4180800`. |
| 11. DM2 con evaluación de pie diabético vigente | Sí | Sí | Exacto | Numerador = `P4190809 + P4170300 + P4190500 + P4190600`; denominador `P4150602`. |
| 12a. DM2 con tamizaje de RD vigente | No exacto | No exacto | Parcial | Hay `P4190950` (fondo de ojo vigente) y `P4302102` (retinopatía diabética), pero no aparece un código explícito de "tamizaje de RD vigente" en el P4 local. |
| 12b. DM2 con fondo de ojo vigente | Sí | Sí | Exacto | Numerador `P4190950`; denominador `P4150602`. |
| 13. HTA con evaluación de función renal | Sí | Sí | Exacto | Numerador `P4301080`; denominador `P4150601`. |
| 14. DM2 con evaluación de función renal | Sí | Sí | Exacto | Numerador `P4301040`; denominador `P4150602`. |
| 15. DM + ERC en tratamiento de prevención secundaria | No exacto | Sí | Exacto solo 2025 | En `2025` se puede con `P4401019 / P4301070`. En `2024` existe una estructura previa (`P4190807` y etapas ERC) que no es equivalente exacta al indicador de la planilla. |
| 16. ECV en tratamiento con antiagregante plaquetario | No exacto | Sí | Exacto solo 2025 | En `2025` se puede con `P4401013 + P4401016` sobre `P4190900 + P4190910`. En `2024` aparece `P4190930`, pero agrupa ECV con otra lógica. |
| 17. ECV en tratamiento con estatinas | No exacto | Sí | Exacto solo 2025 | En `2025` se puede con `P4401014 + P4401017` sobre `P4190900 + P4190910`. En `2024` aparece `P4190940`, pero no es equivalente exacto al desglose de la planilla. |
| 18. Tasa de egresos hospitalarios por enfermedad cerebrovascular | Sí | No | Factible hasta 2024 | Se puede construir con `DIAG1 = G45, I63-I67, I69`, FONASA, RM, 15+; hay datos locales 2020-2024, pero no existe archivo 2025. |
| 19. Tasa de egresos hospitalarios por enfermedades isquémicas del corazón | Sí | No | Factible hasta 2024 | Se puede construir con `DIAG1 = I20-I25`, FONASA, RM, 15+. |
| 20. Tasa de egresos hospitalarios por insuficiencia cardiaca | Sí | No | Factible hasta 2024 | Se puede construir con `DIAG1 = I50 o J81`, FONASA, RM, 15+. |
| 21. Tasa de egresos hospitalarios por diabetes mellitus | Sí | No | Factible hasta 2024 | Se puede construir con `DIAG1 = E11-E14`, FONASA, RM, 15+. |
| 22. Tasa de egresos hospitalarios por amputación del pie diabético | No exacto | No | No exacto / no factible completo | En `2022` existe un **proxy** usando glosas de intervención/procedimiento con amputación y `DIAG1 = E11-E14`, pero `2023-2024` no traen campos de procedimiento y no hay archivo `2025`. |

## Observaciones importantes

- **La Serie P local hoy solo existe para `2024` y `2025`.**
  - Aunque existen carpetas `REM_2022` y `REM_2023`, no está disponible localmente la `SerieP2022.csv` ni la `SerieP2023.csv`.
  - Eso impide reconstruir con exactitud los valores históricos `2019`, `2021`, `2022` y `2023` desde los archivos crudos actuales.

- **Los egresos hospitalarios abiertos sí permiten abrir nuevos indicadores.**
  - Las bases locales cubren `2020-2024`.
  - Para `18-21` existe lo necesario: `DIAG1`, previsión FONASA, grupo etario, región y pertenencia SNSS/no SNSS.
  - Para `22`, la limitación es estructural: `2023-2024` no incluyen glosas de procedimiento/intervención, así que no se puede identificar amputación del pie diabético con la misma lógica del tablero.

- **Supuesto metodológico para `18-21`:**
  - La región disponible en los archivos abiertos es `REGION_RESIDENCIA`.
  - Por lo tanto, la factibilidad local de `18-21` se apoya en el supuesto de que el filtro regional del indicador puede operacionalizarse con región de residencia del egresado.

- **Conteos exploratorios ya verificados en RM, FONASA, 15+**:
  - Indicador `18`: `8.291` egresos en `2022`, `8.976` en `2023`, `10.148` en `2024`
  - Indicador `19`: `9.025` egresos en `2022`, `9.282` en `2023`, `9.569` en `2024`
  - Indicador `20`: `5.871` egresos en `2022`, `5.681` en `2023`, `6.049` en `2024`
  - Indicador `21`: `4.239` egresos en `2022`, `4.394` en `2023`, `5.107` en `2024`
  - Indicador `22`: solo existe un **proxy 2022** con `1.802` registros candidatos, no equivalente exacto al indicador oficial.

- **La población inscrita validada ya quedó preparada para `2023`, `2024` y `2025`.**
  - Total RM 15+ `2023`: `4.419.720`
  - Total RM 15+ `2024`: `4.632.711`
  - Total RM 15+ `2025`: `4.821.389`

- **Los denominadores estimados para cobertura ya se pueden construir:**
  - HTA estimada = población 15+ x `0,276`
  - DM2 estimada = población 15+ x `0,123`

- **No hubo registros sin match con el maestro de establecimientos** en el CSV generado de población inscrita.

- **El CSV principal trae la bandera `es_aps`.**
  - Para cálculos por establecimiento conviene revisar esa columna y, si queremos alinearnos con la lógica APS de otros proyectos REM, privilegiar `es_aps = True`.

## Conclusión práctica

Con lo que existe hoy en local, ya podemos avanzar de forma robusta con:

- indicadores `1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12b, 13, 14` para `2024` y `2025`
- indicadores `15, 16, 17` de forma **exacta en `2025`**
- indicadores `18, 19, 20, 21` de forma **operativa y trazable hasta `2024`**

Todavía no podemos cerrar de forma exacta:

- `5` por depender de otra fuente
- `12a` porque el P4 local no trae un código explícito de tamizaje RD vigente
- `22` porque en los egresos abiertos `2023-2024` faltan campos de procedimiento/intervención, y además no hay archivo `2025`
