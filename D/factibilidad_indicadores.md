# Factibilidad de Indicadores REM-Cardiovascular

## Fuentes de información disponibles

| Fuente | Disponible | Ruta |
|--------|-----------|------|
| **Serie P (REM P4)** - datos 2024 y 2025 | ✅ | `DATA\REM\REM_2024\Datos\SerieP2024.csv` / `REM_2025\Datos\SerieP2025.csv` |
| **Serie A (REM A05)** - datos 2024 y 2025 | ✅ | `DATA\REM\REM_2024\Datos\SerieA2024.csv` / `REM_2025\Datos\SerieA2025.csv` |
| **FONASA T8009** - Población Inscrita Validada APS RM | ✅ | `DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2024 (Base pago 2025)\T8009_Inscritos_RM.xlsx` |
| **Maestro Establecimientos DEIS** | ✅ | `DATA\ESTABLECIMIENTOS\establecimientos_20260424.csv` |
| **Diccionario REM P4** - columnas y códigos | ✅ | `DICCIONARIO CODIGOS SP_24_V1.1.xlsm` / `SP_25_V1.0.xlsm` |
| **Diccionario REM A05** - columnas y códigos | ✅ | `DICCIONARIO CODIGOS SA_24_V1.1.xlsm` / `SA_25_V1.5.xlsm` |
| **DEIS Egresos Hospitalarios** (base datos local) | ✅ | `D:\DATA\EGRESOS_HOSPITALARIOS\EGRESOS_2024\EGRESOS_2024.csv` (y años 2020-2023) |

---

## Estado por indicador

### Indicadores 1-17: Basados en REM P4 + FONASA → VIABLES ✅

| # | Indicador | Numerador | Denominador | Factor | Estado |
|---|-----------|-----------|-------------|--------|--------|
| 1 | **Cobertura HTA** | `P4150601` (Col01) - Personas bajo control HTA | PIV 15+ × 27.6% (prevalencia HTA ENS) | ×100 | ✅ **VIABLE** |
| 2 | **Control HTA** | `P4180200` (Col01) PA<140/90 + `P4200100` (Col01) PA<150/90 (≥80a) | `P4150601` (Col01) - Personas bajo control HTA | ×100 | ✅ **VIABLE** |
| 3 | **Cobertura efectiva HTA** | `P4180200` + `P4200100` | PIV 15+ × 27.6% | ×100 | ✅ **VIABLE** |
| 4 | **HTA muy descompensadas** | `P4200400` (Col01) PA ≥160/100 | `P4150601` (Col01) | ×100 | ✅ **VIABLE** |
| 5 | **Índice de Madurez HEARTS** | `P4190808` (Col01) - Índice Madurez HEARTS | `P4150601` (Col01) | ×100 | ✅ **VIABLE** |
| 6 | **Cobertura DM2** | `P4150602` (Col01) - Personas bajo control DM2 | PIV 15+ × 12.3% (prevalencia DM2 ENS) | ×100 | ✅ **VIABLE** |
| 7 | **Control DM2** | `P4180300` (Col01) HbA1c<7% + `P4200200` (Col01) HbA1c<8% (≥80a) | `P4150602` (Col01) | ×100 | ✅ **VIABLE** |
| 8 | **Cobertura efectiva DM2** | `P4180300` + `P4200200` | PIV 15+ × 12.3% | ×100 | ✅ **VIABLE** |
| 9 | **DM2 muy descompensadas** | `P4190960` (Col01) HbA1c ≥9% | `P4150602` (Col01) | ×100 | ✅ **VIABLE** |
| 10 | **DM2 compensada usuarias insulina** | `P4200700` (Col01) - Insulina que logra meta HbA1c | `P4180800` (Col01) - En tratamiento con insulina | ×100 | ✅ **VIABLE** |
| 11 | **DM2 evaluación pie diabético vigente** | ❌ **Código no identificado en P4** - La Serie P 2024 no tiene código específico para pie diabético (posiblemente incluido en otra sección o código P4 no documentado) | `P4150602` (Col01) | ×100 | ⚠️ **PENDIENTE** - Revisar diccionario SP o buscar P419xxxx adicional |
| 12a | **DM2 tamizaje retinopatía diabética vigente** | ❌ **Código no identificado en P4** - No aparece código específico en la Serie P 2024 para tamizaje de RD. El denominador requiere `P4150602` - personas con DM2 sin retinopatía. | `P4150602` - DM2 sin retinopatía | ×100 | ⚠️ **PENDIENTE** - Requiere identificar código específico |
| 12b | **DM2 evaluación fondo de ojo vigente** | `P4190950` (Col01) - Con fondo de ojo vigente | `P4150602` (Col01) | ×100 | ✅ **VIABLE** |
| 13 | **HTA evaluación función renal** | `P4301080` (Col01) - HTA con VFGe y RAC vigente | `P4150601` (Col01) | ×100 | ✅ **VIABLE** |
| 14 | **DM2 evaluación función renal** | `P4301040` (Col01) - DM con VFGe y RAC vigente | `P4150602` (Col01) | ×100 | ✅ **VIABLE** |
| 15 | **DM + ERC tratamiento prevención secundaria** | `P4200800` (Col01) - ERC con IECA o ARA II | `P4200600` (Col01) - Personas en PSCV con ERC | ×100 | ✅ **VIABLE** |
| 16 | **ECV antiagregante plaquetario** | `P4190930` (Col01) - Antiagregantes plaquetarios | `P4190900` + `P4190910` (IAM + ACV) | ×100 | ✅ **VIABLE** |
| 17 | **ECV estatinas** | `P4190940` (Col01) - En tratamiento con estatina | `P4190900` + `P4190910` (IAM + ACV) | ×100 | ✅ **VIABLE** |

### Indicadores 18-22: Basados en DEIS Egresos Hospitalarios → AHORA VIABLES ✅

| # | Indicador | Filtro CIE-10 (DIAG1) | Denominador | Factor | Egresos RM FONASA 15+ 2024 | Estado |
|---|-----------|----------------------|-------------|--------|:------------------------:|--------|
| 18 | **Tasa egresos hospitalarios por enfermedad cerebrovascular** | `I60` a `I69` | Población FONASA 15+ | ×10.000 | 11.281 | ✅ **VIABLE** |
| 19 | **Tasa egresos hospitalarios por enfermedades isquémicas del corazón** | `I20` a `I25` | Población FONASA 15+ | ×10.000 | 9.574 | ✅ **VIABLE** |
| 20 | **Tasa egresos hospitalarios por insuficiencia cardíaca** | `I50` | Población FONASA 15+ | ×10.000 | 5.463 | ✅ **VIABLE** |
| 21 | **Tasa egresos hospitalarios por diabetes mellitus** | `E10` a `E14` | Población FONASA 15+ | ×10.000 | 6.330 | ✅ **VIABLE** |
| 22 | **Tasa egresos hospitalarios amputación pie diabético** | `E105`, `E115`, `E145` (DM c/ comp. circulatorias periféricas) | Población FONASA 15+ | ×10.000 | 3.377 | ✅ **VIABLE** (proxy) |

**Detalle del indicador 22:** No existen códigos de procedimiento en esta base de datos. Se usa como proxy `E10.5`/`E11.5`/`E14.5` (DM con complicaciones circulatorias periféricas), que es el estándar para pie diabético con amputación en fuentes DEIS. La planilla original referencia al "Tablero PSCV DEIS", que probablemente usa esta misma codificación.

**Estructura de datos disponible:**
- Archivos por año: `EGRESOS_2020` a `EGRESOS_2024` (~1.3M a 1.7M registros/año)
- Columnas clave: `REGION_RESIDENCIA` (código región), `PREVISION` (1=FONASA), `GRUPO_EDAD`, `DIAG1` (CIE-10), `SEXO`, `DIAS_ESTADA`, `CONDICION_EGRESO`
- Cobertura RM (2024): 648.390 egresos totales, 422.896 FONASA 15+

---

## Resumen

| Estado | Cantidad | Indicadores |
|--------|----------|-------------|
| ✅ **VIABLE** | 15 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12b, 13, 14, 15, 16, 17 |
| ⚠️ **PENDIENTE** | 2 | 11 (pie diabético), 12a (tamizaje RD) |
| ✅ **VIABLE** | 20 | 1-10, 12b-22 |
| ⚠️ **PENDIENTE** | 2 | 11 (pie diabético), 12a (tamizaje RD) |

**Total indicadores en planilla:** 22 (considerando que el 12 tiene dos variantes)
**Indicadores factibles con datos actuales:** 20 de 22 (91%)

## Notas sobre indicadores pendientes (11 y 12a)

- **Indicador 11 (pie diabético)**: No se encontró código P4 específico en la Serie P 2024. Posibles candidatos a revisar en el diccionario SP: `P419xxxx` de la sección de seguimiento de DM2.
- **Indicador 12a (tamizaje RD)**: Similar al anterior. El denominador requiere `P4150602` - personas con DM2 **sin retinopatía**, lo que implica un código adicional no identificado.
- **Indicador 12b (fondo de ojo)**: Sí está disponible mediante `P4190950` y es una alternativa al tamizaje de RD.
