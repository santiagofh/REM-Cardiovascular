from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular"
)
OUTPUT_DIR = ROOT / "2025"
MASTER_PATH = Path(
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\ESTABLECIMIENTOS\establecimientos_20260424.csv"
)
SERIE_P_PATHS = {
    2024: Path(
        r"D:\DATA\REM\REM_2024\Datos\SerieP2024.csv"
    ),
    2025: Path(
        r"D:\DATA\REM\REM_2025\Datos\SerieP2025.csv"
    ),
}
PIV_ESTABLECIMIENTO_PATH = (
    OUTPUT_DIR / "poblacion_inscrita_validada_15_mas_rm_establecimiento_2023_2025.csv"
)
PANEL_REFERENCIA_PATH = OUTPUT_DIR / "indicadores_cardiovascular_panel_2026.csv"
CSV_ENCODING = "utf-8-sig"

GEO_COLUMNS = [
    "Ano",
    "IdServicio",
    "servicio_salud",
    "IdComuna",
    "comuna",
    "IdEstablecimiento",
    "establecimiento",
    "tipo_establecimiento",
    "dependencia",
    "nivel_atencion",
    "estado_funcionamiento",
    "es_aps",
]

INDICATOR_DEFINITIONS = [
    {
        "indicador_id": "1",
        "nombre_indicador": "Cobertura de hipertensión arterial (HTA)",
        "grupo_indicador": "HTA y HEARTS",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4150601"],
        "denominator_kind": "piv_hta_aps",
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total; numerador con todos los reportantes REM P4 RM y denominador PIV APS.",
    },
    {
        "indicador_id": "2",
        "nombre_indicador": "Control de HTA",
        "grupo_indicador": "HTA y HEARTS",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4180200", "P4200100"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150601"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "3",
        "nombre_indicador": "Cobertura efectiva (tasa de control poblacional) de HTA",
        "grupo_indicador": "HTA y HEARTS",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4180200", "P4200100"],
        "denominator_kind": "piv_hta_aps",
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total; numerador con todos los reportantes REM P4 RM y denominador PIV APS.",
    },
    {
        "indicador_id": "4",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de HTA, muy descompensadas",
        "grupo_indicador": "HTA y HEARTS",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4200400"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150601"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "6",
        "nombre_indicador": "Cobertura de diabetes mellitus tipo 2 (DM2)",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4150602"],
        "denominator_kind": "piv_dm2_aps",
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total; numerador con todos los reportantes REM P4 RM y denominador PIV APS.",
    },
    {
        "indicador_id": "7",
        "nombre_indicador": "Control de DM2",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4180300", "P4200200"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150602"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "8",
        "nombre_indicador": "Cobertura efectiva (tasa de control poblacional) de DM2",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4180300", "P4200200"],
        "denominator_kind": "piv_dm2_aps",
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total; numerador con todos los reportantes REM P4 RM y denominador PIV APS.",
    },
    {
        "indicador_id": "9",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de DM2, muy descompensadas",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4190960"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150602"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "10",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de DM2, compensada, usuarias de insulina",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4200700"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4180800"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "11",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de DM2, con evaluación de pie diabético vigente",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4190809", "P4170300", "P4190500", "P4190600"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150602"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "12b",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de DM2, con evaluación de fondo de ojo vigente",
        "grupo_indicador": "DM2 y seguimiento",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4190950"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150602"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "13",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de HTA, con evaluación de función renal",
        "grupo_indicador": "Función renal y ERC",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4301080"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150601"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "14",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de DM2, con evaluación de función renal",
        "grupo_indicador": "Función renal y ERC",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4301040"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4150602"],
        "years": [2024, 2025],
        "estado_2024": "calculado",
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "15",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de DM y ERC en tratamiento de prevención secundaria de ERC",
        "grupo_indicador": "Función renal y ERC",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4401019"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4301070"],
        "years": [2025],
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "16",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de ECV, en tratamiento con antiagregante plaquetario",
        "grupo_indicador": "ECV y prevención secundaria",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4401013", "P4401016"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4190900", "P4190910"],
        "years": [2024, 2025],
        "year_overrides": {
            2024: {
                "numerator_codes": ["P4190930"],
                "estado": "proxy",
                "metodo": "Proxy 2024 con código consolidado previo P4190930, Mes 12, Col01 total.",
            }
        },
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
    {
        "indicador_id": "17",
        "nombre_indicador": "Porcentaje de personas con diagnóstico de ECV, en tratamiento con estatinas",
        "grupo_indicador": "ECV y prevención secundaria",
        "unidad": "%",
        "numerator_kind": "rem",
        "numerator_codes": ["P4401014", "P4401017"],
        "denominator_kind": "rem",
        "denominator_codes": ["P4190900", "P4190910"],
        "years": [2024, 2025],
        "year_overrides": {
            2024: {
                "numerator_codes": ["P4190940"],
                "estado": "proxy",
                "metodo": "Proxy 2024 con código consolidado previo P4190940, Mes 12, Col01 total.",
            }
        },
        "estado_2025": "calculado",
        "metodo": "Mes 12, Col01 total.",
    },
]


def code_text(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )


def load_master_lookup() -> pd.DataFrame:
    cols = [
        "EstablecimientoCodigoAntiguo",
        "EstablecimientoCodigo",
        "SeremiSaludCodigo_ServicioDeSaludCodigo",
        "SeremiSaludGlosa_ServicioDeSaludGlosa",
        "TipoEstablecimientoGlosa",
        "EstablecimientoGlosa",
        "DependenciaAdministrativa",
        "NivelAtencionEstabglosa",
        "ComunaCodigo",
        "ComunaGlosa",
        "EstadoFuncionamiento",
    ]
    master = pd.read_csv(MASTER_PATH, sep=";", dtype=str, usecols=cols)
    for column in [
        "EstablecimientoCodigoAntiguo",
        "EstablecimientoCodigo",
        "SeremiSaludCodigo_ServicioDeSaludCodigo",
        "ComunaCodigo",
    ]:
        master[column] = code_text(master[column])

    current_codes = master.assign(IdEstablecimiento_lookup=master["EstablecimientoCodigo"])
    old_codes = master.assign(IdEstablecimiento_lookup=master["EstablecimientoCodigoAntiguo"])
    lookup = pd.concat([current_codes, old_codes], ignore_index=True)
    lookup = lookup[lookup["IdEstablecimiento_lookup"].ne("")]
    lookup = lookup.drop_duplicates("IdEstablecimiento_lookup")
    lookup["es_aps"] = lookup["NivelAtencionEstabglosa"].fillna("").str.contains(
        "Primario",
        case=False,
        na=False,
    )
    return lookup


def load_population_aps() -> pd.DataFrame:
    pop = pd.read_csv(PIV_ESTABLECIMIENTO_PATH, dtype=str)
    numeric_columns = [
        "AnoIndicador",
        "poblacion_estimada_hta_15_mas",
        "poblacion_estimada_dm2_15_mas",
        "poblacion_inscrita_validada_15_mas",
    ]
    for column in numeric_columns:
        pop[column] = pd.to_numeric(pop[column], errors="coerce")

    pop["es_aps"] = (
        pop["es_aps"].astype(str).str.strip().str.lower().map({"true": True, "false": False})
    )
    pop = pop[pop["es_aps"] == True].copy()
    pop["Ano"] = pd.to_numeric(pop["AnoIndicador"], errors="coerce").astype("Int64")
    pop["IdEstablecimiento"] = code_text(pop["IdEstablecimiento"])
    pop["IdServicio"] = code_text(pop["IdServicio_master"])
    pop["IdComuna"] = code_text(pop["IdComuna_master"])
    pop["servicio_salud"] = pop["servicio_salud_master"].fillna("").astype(str).str.strip()
    pop["comuna"] = pop["comuna_master"].fillna("").astype(str).str.strip()
    pop["establecimiento"] = pop["establecimiento_master"].fillna("").astype(str).str.strip()
    pop["tipo_establecimiento"] = pop["tipo_establecimiento_master"].fillna("").astype(str).str.strip()
    pop["dependencia"] = pop["dependencia_master"].fillna("").astype(str).str.strip()
    pop["nivel_atencion"] = pop["nivel_atencion_master"].fillna("").astype(str).str.strip()
    pop["estado_funcionamiento"] = (
        pop["estado_funcionamiento_master"].fillna("").astype(str).str.strip()
    )
    return pop


def relevant_codes() -> list[str]:
    codes: set[str] = set()
    for definition in INDICATOR_DEFINITIONS:
        codes.update(definition.get("numerator_codes", []))
        codes.update(definition.get("denominator_codes", []))
        for override in definition.get("year_overrides", {}).values():
            codes.update(override.get("numerator_codes", []))
            codes.update(override.get("denominator_codes", []))
    return sorted(codes)


def load_rem_year(year: int, lookup: pd.DataFrame, codes: list[str]) -> pd.DataFrame:
    path = SERIE_P_PATHS[year]
    rem = pd.read_csv(
        path,
        sep=";",
        usecols=[
            "Mes",
            "Ano",
            "IdServicio",
            "IdRegion",
            "IdComuna",
            "IdEstablecimiento",
            "CodigoPrestacion",
            "Col01",
        ],
        dtype={"CodigoPrestacion": "string", "IdEstablecimiento": "string"},
        low_memory=False,
    )
    rem = rem[
        rem["Mes"].eq(12)
        & rem["IdRegion"].eq(13)
        & rem["CodigoPrestacion"].isin(codes)
    ].copy()

    rem["Ano"] = pd.to_numeric(rem["Ano"], errors="coerce").astype("Int64")
    rem["IdServicio"] = code_text(rem["IdServicio"])
    rem["IdComuna"] = code_text(rem["IdComuna"])
    rem["IdEstablecimiento"] = code_text(rem["IdEstablecimiento"])
    rem["CodigoPrestacion"] = rem["CodigoPrestacion"].astype(str).str.strip()
    rem["Col01"] = pd.to_numeric(rem["Col01"], errors="coerce").fillna(0)

    rem = rem.merge(
        lookup[
            [
                "IdEstablecimiento_lookup",
                "SeremiSaludCodigo_ServicioDeSaludCodigo",
                "SeremiSaludGlosa_ServicioDeSaludGlosa",
                "ComunaCodigo",
                "ComunaGlosa",
                "EstablecimientoGlosa",
                "TipoEstablecimientoGlosa",
                "DependenciaAdministrativa",
                "NivelAtencionEstabglosa",
                "EstadoFuncionamiento",
                "es_aps",
            ]
        ],
        left_on="IdEstablecimiento",
        right_on="IdEstablecimiento_lookup",
        how="left",
    )

    rem["IdServicio"] = code_text(
        rem["SeremiSaludCodigo_ServicioDeSaludCodigo"].fillna(rem["IdServicio"])
    )
    rem["servicio_salud"] = (
        rem["SeremiSaludGlosa_ServicioDeSaludGlosa"].fillna("").astype(str).str.strip()
    )
    rem.loc[rem["servicio_salud"].eq(""), "servicio_salud"] = (
        "Servicio " + rem["IdServicio"].fillna("").astype(str)
    )
    rem["IdComuna"] = code_text(rem["ComunaCodigo"].fillna(rem["IdComuna"]))
    rem["comuna"] = rem["ComunaGlosa"].fillna("").astype(str).str.strip()
    rem.loc[rem["comuna"].eq(""), "comuna"] = "Comuna " + rem["IdComuna"].astype(str)
    rem["establecimiento"] = rem["EstablecimientoGlosa"].fillna("").astype(str).str.strip()
    rem.loc[rem["establecimiento"].eq(""), "establecimiento"] = (
        "Establecimiento " + rem["IdEstablecimiento"].astype(str)
    )
    rem["tipo_establecimiento"] = (
        rem["TipoEstablecimientoGlosa"].fillna("").astype(str).str.strip()
    )
    rem["dependencia"] = rem["DependenciaAdministrativa"].fillna("").astype(str).str.strip()
    rem["nivel_atencion"] = rem["NivelAtencionEstabglosa"].fillna("").astype(str).str.strip()
    rem["estado_funcionamiento"] = rem["EstadoFuncionamiento"].fillna("").astype(str).str.strip()
    rem["es_aps"] = rem["es_aps"].fillna(False)

    aggregated = (
        rem.groupby(
            GEO_COLUMNS + ["CodigoPrestacion"],
            dropna=False,
            as_index=False,
        )["Col01"]
        .sum()
        .rename(columns={"Col01": "valor_col01"})
    )
    return aggregated


def aggregate_codes(
    df: pd.DataFrame,
    code_column: str,
    codes: list[str],
    value_name: str,
) -> pd.DataFrame:
    if not codes:
        return pd.DataFrame(columns=GEO_COLUMNS + [value_name])
    subset = df[df[code_column].isin(codes)].copy()
    if subset.empty:
        return pd.DataFrame(columns=GEO_COLUMNS + [value_name])
    return (
        subset.groupby(GEO_COLUMNS, dropna=False, as_index=False)["valor_col01"]
        .sum()
        .rename(columns={"valor_col01": value_name})
    )


def resolve_definition(definition: dict[str, object], year: int) -> dict[str, object] | None:
    if year not in definition["years"]:
        return None

    resolved = {
        "indicador_id": definition["indicador_id"],
        "nombre_indicador": definition["nombre_indicador"],
        "grupo_indicador": definition["grupo_indicador"],
        "unidad": definition["unidad"],
        "numerator_kind": definition["numerator_kind"],
        "numerator_codes": list(definition.get("numerator_codes", [])),
        "denominator_kind": definition["denominator_kind"],
        "denominator_codes": list(definition.get("denominator_codes", [])),
        "estado": definition.get(f"estado_{year}", "calculado"),
        "metodo": definition["metodo"],
    }

    override = definition.get("year_overrides", {}).get(year)
    if override:
        if "numerator_codes" in override:
            resolved["numerator_codes"] = list(override["numerator_codes"])
        if "denominator_codes" in override:
            resolved["denominator_codes"] = list(override["denominator_codes"])
        if "estado" in override:
            resolved["estado"] = override["estado"]
        if "metodo" in override:
            resolved["metodo"] = override["metodo"]

    return resolved


def build_piv_base(pop: pd.DataFrame, year: int, denominator_column: str) -> pd.DataFrame:
    subset = pop[pop["Ano"].eq(year)].copy()
    subset = subset[
        GEO_COLUMNS + [denominator_column]
    ].rename(columns={denominator_column: "denominador"})
    subset["denominador"] = pd.to_numeric(subset["denominador"], errors="coerce").fillna(0)
    subset["denominador_directo"] = subset["denominador"].gt(0)
    return subset


def build_rem_indicator_base(
    rem_year: pd.DataFrame,
    pop: pd.DataFrame,
    definition: dict[str, object],
    year: int,
) -> pd.DataFrame:
    numerator_df = aggregate_codes(
        rem_year,
        "CodigoPrestacion",
        definition["numerator_codes"],
        "numerador",
    )
    numerator_df["rem_reporta"] = numerator_df["numerador"].gt(0)

    if definition["denominator_kind"] == "rem":
        denominator_df = aggregate_codes(
            rem_year,
            "CodigoPrestacion",
            definition["denominator_codes"],
            "denominador",
        )
        base = numerator_df.merge(denominator_df, on=GEO_COLUMNS, how="outer")
        base["numerador"] = pd.to_numeric(base["numerador"], errors="coerce").fillna(0)
        base["denominador"] = pd.to_numeric(base["denominador"], errors="coerce").fillna(0)
        base["rem_reporta"] = base["rem_reporta"].fillna(base["numerador"].gt(0))
        base["denominador_directo"] = base["denominador"].gt(0)
    elif definition["denominator_kind"] == "piv_hta_aps":
        denominator_df = build_piv_base(pop, year, "poblacion_estimada_hta_15_mas")
        base = numerator_df.merge(denominator_df, on=GEO_COLUMNS, how="outer")
        base["numerador"] = pd.to_numeric(base["numerador"], errors="coerce").fillna(0)
        base["denominador"] = pd.to_numeric(base["denominador"], errors="coerce").fillna(0)
        base["rem_reporta"] = base["rem_reporta"].fillna(base["numerador"].gt(0))
        base["denominador_directo"] = base["denominador_directo"].fillna(base["denominador"].gt(0))
    elif definition["denominator_kind"] == "piv_dm2_aps":
        denominator_df = build_piv_base(pop, year, "poblacion_estimada_dm2_15_mas")
        base = numerator_df.merge(denominator_df, on=GEO_COLUMNS, how="outer")
        base["numerador"] = pd.to_numeric(base["numerador"], errors="coerce").fillna(0)
        base["denominador"] = pd.to_numeric(base["denominador"], errors="coerce").fillna(0)
        base["rem_reporta"] = base["rem_reporta"].fillna(base["numerador"].gt(0))
        base["denominador_directo"] = base["denominador_directo"].fillna(base["denominador"].gt(0))
    else:
        raise ValueError(f"Tipo de denominador no soportado: {definition['denominator_kind']}")

    base["Ano"] = pd.to_numeric(base["Ano"], errors="coerce").astype("Int64")
    base["indicador_id"] = definition["indicador_id"]
    base["nombre_indicador"] = definition["nombre_indicador"]
    base["grupo_indicador"] = definition["grupo_indicador"]
    base["unidad"] = definition["unidad"]
    base["estado_calculo"] = definition["estado"]
    base["metodo_calculo"] = definition["metodo"]
    return base


def aggregate_levels(base: pd.DataFrame) -> list[pd.DataFrame]:
    outputs: list[pd.DataFrame] = []
    common_meta = [
        "indicador_id",
        "nombre_indicador",
        "grupo_indicador",
        "unidad",
        "estado_calculo",
        "metodo_calculo",
    ]

    level_specs = {
        "rm": ["Ano"],
        "servicio_salud": ["Ano", "IdServicio", "servicio_salud"],
        "comuna": ["Ano", "IdServicio", "servicio_salud", "IdComuna", "comuna"],
        "establecimiento": GEO_COLUMNS,
    }

    for level_name, group_cols in level_specs.items():
        grouped = (
            base.groupby(group_cols + common_meta, dropna=False, as_index=False)
            .agg(
                numerador=("numerador", "sum"),
                denominador=("denominador", "sum"),
                establecimientos_reportantes=("rem_reporta", lambda s: int(pd.Series(s).fillna(False).sum())),
                establecimientos_con_denominador=(
                    "denominador_directo",
                    lambda s: int(pd.Series(s).fillna(False).sum()),
                ),
            )
        )
        grouped["nivel"] = level_name
        grouped["calculable"] = grouped["denominador"].gt(0)
        grouped["valor"] = (
            grouped["numerador"] / grouped["denominador"] * 100
        ).where(grouped["calculable"])
        outputs.append(grouped)

    return outputs


def build_reference_validation(rm_df: pd.DataFrame) -> pd.DataFrame:
    if not PANEL_REFERENCIA_PATH.exists():
        return pd.DataFrame()

    reference = pd.read_csv(PANEL_REFERENCIA_PATH, dtype=str).fillna("")
    reference["valor_2024_rm_num"] = pd.to_numeric(reference["valor_2024_rm"], errors="coerce")
    ref_subset = reference[reference["valor_2024_rm_num"].notna()].copy()
    ref_subset["indicador_id"] = ref_subset["indicador_id"].astype(str).str.strip()

    calc_2024 = rm_df[rm_df["Ano"].eq(2024)].copy()
    merged = calc_2024.merge(
        ref_subset[["indicador_id", "nombre_indicador", "valor_2024_rm_num"]],
        on="indicador_id",
        how="left",
        suffixes=("", "_referencia"),
    )
    merged["diferencia_pp"] = merged["valor"] - (merged["valor_2024_rm_num"] * 100)
    return merged[
        [
            "Ano",
            "indicador_id",
            "nombre_indicador",
            "estado_calculo",
            "numerador",
            "denominador",
            "valor",
            "valor_2024_rm_num",
            "diferencia_pp",
        ]
    ].rename(
        columns={
            "valor": "valor_calculado_pct",
            "valor_2024_rm_num": "valor_referencia_2024_rm_proporcion",
        }
    )


def build_indicator_catalog() -> pd.DataFrame:
    rows = []
    for definition in INDICATOR_DEFINITIONS:
        years = ",".join(str(year) for year in definition["years"])
        rows.append(
            {
                "indicador_id": definition["indicador_id"],
                "nombre_indicador": definition["nombre_indicador"],
                "grupo_indicador": definition["grupo_indicador"],
                "unidad": definition["unidad"],
                "anios_disponibles": years,
                "metodo_base": definition["metodo"],
            }
        )
    return pd.DataFrame(rows).sort_values("indicador_id")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lookup = load_master_lookup()
    population_aps = load_population_aps()
    codes = relevant_codes()

    rem_frames = [load_rem_year(year, lookup, codes) for year in SERIE_P_PATHS]
    rem_all = pd.concat(rem_frames, ignore_index=True)

    indicator_bases: list[pd.DataFrame] = []
    indicator_levels: list[pd.DataFrame] = []
    for year in sorted(SERIE_P_PATHS):
        rem_year = rem_all[rem_all["Ano"].eq(year)].copy()
        for definition in INDICATOR_DEFINITIONS:
            resolved = resolve_definition(definition, year)
            if resolved is None:
                continue
            base = build_rem_indicator_base(rem_year, population_aps, resolved, year)
            indicator_bases.append(base)
            indicator_levels.extend(aggregate_levels(base))

    base_df = pd.concat(indicator_bases, ignore_index=True)
    dashboard_df = pd.concat(indicator_levels, ignore_index=True)
    dashboard_df["valor_orden"] = pd.to_numeric(dashboard_df["valor"], errors="coerce")

    rm_df = dashboard_df[dashboard_df["nivel"].eq("rm")].copy()
    validation_df = build_reference_validation(rm_df)
    catalog_df = build_indicator_catalog()

    paths = {
        "rem_componentes": OUTPUT_DIR / "rem_p4_cardiovascular_col01_mes12_2024_2025.csv",
        "indicadores_base": OUTPUT_DIR / "indicadores_cardiovascular_base_establecimiento_2024_2025.csv",
        "dashboard": OUTPUT_DIR / "indicadores_cardiovascular_dashboard_2024_2025.csv",
        "rm": OUTPUT_DIR / "indicadores_cardiovascular_rm_2024_2025.csv",
        "validacion": OUTPUT_DIR / "indicadores_cardiovascular_validacion_rm_2024.csv",
        "catalogo": OUTPUT_DIR / "indicadores_cardiovascular_catalogo_2024_2025.csv",
        "metadata": OUTPUT_DIR / "indicadores_cardiovascular_calculo_metadata_2024_2025.json",
    }

    rem_all.to_csv(paths["rem_componentes"], index=False, encoding=CSV_ENCODING)
    base_df.to_csv(paths["indicadores_base"], index=False, encoding=CSV_ENCODING)
    dashboard_df.to_csv(paths["dashboard"], index=False, encoding=CSV_ENCODING)
    rm_df.to_csv(paths["rm"], index=False, encoding=CSV_ENCODING)
    if not validation_df.empty:
        validation_df.to_csv(paths["validacion"], index=False, encoding=CSV_ENCODING)
    catalog_df.to_csv(paths["catalogo"], index=False, encoding=CSV_ENCODING)

    paths["metadata"].write_text(
        json.dumps(
            {
                "generado_en": pd.Timestamp.now().isoformat(),
                "alcance": "Indicadores cardiovasculares calculados desde Serie P mes 12 y población inscrita validada APS.",
                "serie_p_fuentes": {str(year): str(path) for year, path in SERIE_P_PATHS.items()},
                "poblacion_fuente": str(PIV_ESTABLECIMIENTO_PATH),
                "maestro_fuente": str(MASTER_PATH),
                "indicadores_incluidos": [
                    {
                        "indicador_id": definition["indicador_id"],
                        "nombre_indicador": definition["nombre_indicador"],
                        "anios": definition["years"],
                    }
                    for definition in INDICATOR_DEFINITIONS
                ],
                "archivos_generados": {name: str(path) for name, path in paths.items()},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "dashboard_rows": int(len(dashboard_df)),
                "rm_rows": int(len(rm_df)),
                "indicadores": sorted(dashboard_df["indicador_id"].unique().tolist()),
                "niveles": sorted(dashboard_df["nivel"].unique().tolist()),
                "archivo_dashboard": str(paths["dashboard"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
