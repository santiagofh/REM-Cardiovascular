from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
CONFIG_PATH = ROOT / "diccionario_rem_cardiovascular.json"
POBLACION_CONFIG_PATH = ROOT / "diccionario_poblacion_inscrita.json"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_poblacion_config() -> dict:
    with POBLACION_CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def code_text(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )


def to_int_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype("int64")


# ─────────────────────────────────────────────
# 1. MAESTRO DE ESTABLECIMIENTOS
# ─────────────────────────────────────────────


def build_master_lookup(master_path: Path) -> pd.DataFrame:
    cols = [
        "EstablecimientoCodigoAntiguo",
        "EstablecimientoCodigo",
        "EstablecimientoCodigoMadreNuevo",
        "RegionCodigo",
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
    master = pd.read_csv(master_path, sep=";", dtype=str, usecols=cols)
    for col in [
        "EstablecimientoCodigoAntiguo",
        "EstablecimientoCodigo",
        "EstablecimientoCodigoMadreNuevo",
        "RegionCodigo",
        "SeremiSaludCodigo_ServicioDeSaludCodigo",
        "ComunaCodigo",
    ]:
        master[col] = code_text(master[col])

    current = master.assign(IdEstablecimiento_lookup=master["EstablecimientoCodigo"])
    old = master.assign(IdEstablecimiento_lookup=master["EstablecimientoCodigoAntiguo"])
    lookup = pd.concat([current, old], ignore_index=True)
    lookup = lookup[lookup["IdEstablecimiento_lookup"].ne("")]
    lookup = lookup.drop_duplicates("IdEstablecimiento_lookup")
    lookup["es_aps"] = (
        lookup["NivelAtencionEstabglosa"].fillna("").str.contains("Primario", case=False, na=False)
    )
    return lookup


def merge_master(df: pd.DataFrame, master: pd.DataFrame, id_col: str = "IdEstablecimiento") -> pd.DataFrame:
    out = df.merge(
        master,
        left_on=id_col,
        right_on="IdEstablecimiento_lookup",
        how="left",
    ).drop(columns=["IdEstablecimiento_lookup"])
    rename_map = {
        "EstablecimientoCodigo": "EstablecimientoCodigo_master",
        "EstablecimientoCodigoMadreNuevo": "codigo_madre_master",
        "SeremiSaludCodigo_ServicioDeSaludCodigo": "IdServicio_master",
        "SeremiSaludGlosa_ServicioDeSaludGlosa": "servicio_salud_master",
        "TipoEstablecimientoGlosa": "tipo_establecimiento_master",
        "EstablecimientoGlosa": "establecimiento_master",
        "DependenciaAdministrativa": "dependencia_master",
        "NivelAtencionEstabglosa": "nivel_atencion_master",
        "ComunaCodigo": "IdComuna_master",
        "ComunaGlosa": "comuna_master",
        "EstadoFuncionamiento": "estado_funcionamiento_master",
    }
    out = out.rename(columns=rename_map)
    out["sin_match_master"] = out["establecimiento_master"].isna()
    return out


# ─────────────────────────────────────────────
# 2. NUMERADOR - SERIE P (REM P4)
# ─────────────────────────────────────────────

P4_CODES_INDICADORES = {
    # Seccion A - Personas bajo control
    "P4150601": "HTA - Personas bajo control",
    "P4150602": "DM2 - Personas bajo control",
    "P4150603": "Dislipidemia - Personas bajo control",
    "P4150100": "Numero de personas en PSCV",
    # Seccion A - Riesgo Cardiovascular
    "P4190809": "Riesgo cardiovascular bajo",
    "P4170300": "Riesgo cardiovascular moderado",
    "P4190500": "Riesgo cardiovascular alto",
    "P4190600": "Riesgo cardiovascular maximo",
    "P4190808": "Indice de Madurez HEARTS",
    # Seccion A - Antecedentes ECV
    "P4190900": "IAM - Antecedentes",
    "P4190910": "ACV - Antecedentes",
    # Seccion A - ERC
    "P4200600": "Personas en PSCV con ERC",
    "P4200800": "ERC con IECA o ARA II",
    "P4200300": "ERC estadio 3b, 4 y 5",
    "P4201600": "Personas en PSCV con diagnostico de ERC",
    "P4201700": "ERC estadio 3b con filtrado descendiendo",
    # Seccion B - Metas de Compensacion
    "P4180200": "PA < 140/90 mmHg",
    "P4200100": "PA < 150/90 mmHg (>= 80 a)",
    "P4180300": "HbA1c < 7%",
    "P4200200": "HbA1c < 8% (>= 80 a)",
    "P4190920": "Triple meta (HbA1c, PA, LDL)",
    "P4190930": "Antiagregantes plaquetarios",
    "P4190940": "Estatina",
    "P4190950": "Fondo de ojo vigente",
    "P4180800": "En tratamiento con insulina",
    "P4200700": "Insulina que logra meta HbA1c",
    "P4190960": "HbA1c >= 9% (muy descompensada)",
    # Seccion C - Seguimiento
    "P4200400": "PA >= 160/100 mmHg (muy descompensada)",
    # Funcion renal
    "P4301040": "DM con VFGe y RAC vigente",
    "P4301080": "HTA con VFGe y RAC vigente",
    # Otros
    "P4190800": "Poblacion con evaluacion de RCV",
    "P4190801": "RCV muy bajo (HEARTS)",
    "P4190803": "RCV bajo (HEARTS)",
    "P4190804": "RCV moderado (HEARTS)",
    "P4190805": "RCV alto (HEARTS)",
    "P4190806": "RCV muy alto (HEARTS)",
}

GRUPOS_P4 = {
    "15_19": {"cols": ["Col04", "Col05"], "label": "15 a 19"},
    "20_24": {"cols": ["Col06", "Col07"], "label": "20 a 24"},
    "25_29": {"cols": ["Col08", "Col09"], "label": "25 a 29"},
    "30_34": {"cols": ["Col10", "Col11"], "label": "30 a 34"},
    "35_39": {"cols": ["Col12", "Col13"], "label": "35 a 39"},
    "40_44": {"cols": ["Col14", "Col15"], "label": "40 a 44"},
    "45_49": {"cols": ["Col16", "Col17"], "label": "45 a 49"},
    "50_54": {"cols": ["Col18", "Col19"], "label": "50 a 54"},
    "55_59": {"cols": ["Col20", "Col21"], "label": "55 a 59"},
    "60_64": {"cols": ["Col22", "Col23"], "label": "60 a 64"},
    "65_69": {"cols": ["Col24", "Col25"], "label": "65 a 69"},
    "70_74": {"cols": ["Col26", "Col27"], "label": "70 a 74"},
    "75_79": {"cols": ["Col28", "Col29"], "label": "75 a 79"},
    "80_mas": {"cols": ["Col30", "Col31"], "label": "80 y mas"},
}


TARGET_MONTH = 12


def group_age_sum(df: pd.DataFrame, columns: list[str], output_col: str) -> None:
    existing = [c for c in columns if c in df.columns]
    df[output_col] = df[existing].sum(axis=1) if existing else 0


def extract_numerador_p4(config: dict, master: pd.DataFrame) -> pd.DataFrame:
    series_p = config["input_paths"]["series_p"]
    region = config["region_objetivo"]
    valid_codes = set(P4_CODES_INDICADORES.keys())

    usecols = [
        "Mes", "IdServicio", "Ano", "IdEstablecimiento",
        "CodigoPrestacion", "IdRegion", "IdComuna",
    ] + [f"Col{i:02d}" for i in range(1, 36)]

    frames = []
    for year, raw_path in series_p.items():
        path = Path(os.environ.get(f"SERIE_P_{year}_PATH", raw_path))
        for chunk in pd.read_csv(
            path, sep=";", dtype=str, usecols=usecols, chunksize=250_000, encoding="utf-8-sig",
        ):
            mask = chunk["CodigoPrestacion"].isin(valid_codes) & chunk["IdRegion"].eq(region)
            filtered = chunk[mask].copy()
            if filtered.empty:
                continue
            filtered["Ano"] = year
            mes_int = pd.to_numeric(filtered["Mes"], errors="coerce")
            filtered = filtered[mes_int == TARGET_MONTH].copy()
            frames.append(filtered)

    if not frames:
        raise FileNotFoundError("No se encontraron registros P4 para los codigos solicitados.")

    detail = pd.concat(frames, ignore_index=True)
    for col in ["Mes", "Ano", "IdServicio", "IdRegion", "IdComuna"]:
        detail[col] = to_int_series(detail[col])
    detail["IdEstablecimiento"] = code_text(detail["IdEstablecimiento"])
    detail["CodigoPrestacion"] = code_text(detail["CodigoPrestacion"])
    for col in [f"Col{i:02d}" for i in range(1, 36)]:
        detail[col] = to_int_series(detail[col])

    detail = merge_master(detail, master)
    return detail


# ─────────────────────────────────────────────
# 3. NUMERADOR - SERIE A (REM A05 H/I)
# ─────────────────────────────────────────────

A05_CODES_PSCV = {
    # Ingresos PSCV - Seccion H
    "03030360": "Ingresos al PSCV",
    "03021106": "Ingreso PSCV - HTA",
    "03021107": "Ingreso PSCV - DM2",
    "03021108": "Ingreso PSCV - Dislipidemia",
    "05990071": "Ingreso PSCV - IAM",
    "05990072": "Ingreso PSCV - Otras ECV",
    "09600292": "Ingreso PSCV - ACV",
    "09600293": "Ingreso PSCV - ERC",
    "05810432": "Ingreso PSCV - Tabaquismo >=55",
    "09600294": "Ingreso PSCV - Protocolo HEARTS",
    # Egresos PSCV - Seccion I
    "05810040": "Egresos del PSCV",
    "05225400": "Egreso PSCV - HTA",
    "05225401": "Egreso PSCV - DM2",
    "05225402": "Egreso PSCV - Dislipidemia",
    "05990073": "Egreso PSCV - IAM",
    "05990074": "Egreso PSCV - Otras ECV",
    "09600295": "Egreso PSCV - ACV",
    "09600296": "Egreso PSCV - ERC",
    "05810434": "Egreso PSCV - Tabaquismo >=55",
}


def extract_numerador_a05(config: dict, master: pd.DataFrame) -> pd.DataFrame:
    series_a = config["input_paths"]["series_a"]
    region = config["region_objetivo"]
    valid_codes = set(A05_CODES_PSCV.keys())

    usecols = [
        "Mes", "IdServicio", "Ano", "IdEstablecimiento",
        "CodigoPrestacion", "IdRegion", "IdComuna",
    ] + [f"Col{i:02d}" for i in range(1, 21)]

    frames = []
    for year, raw_path in series_a.items():
        path = Path(os.environ.get(f"SERIE_A_{year}_PATH", raw_path))
        for chunk in pd.read_csv(
            path, sep=";", dtype=str, usecols=usecols, chunksize=250_000, encoding="utf-8-sig",
        ):
            mask = chunk["CodigoPrestacion"].isin(valid_codes) & chunk["IdRegion"].eq(region)
            filtered = chunk[mask].copy()
            if filtered.empty:
                continue
            filtered["Ano"] = year
            frames.append(filtered)

    if not frames:
        print("[AVISO] No se encontraron registros A05 para codigos PSCV.")
        return pd.DataFrame()

    detail = pd.concat(frames, ignore_index=True)
    for col in ["Mes", "Ano", "IdServicio", "IdRegion", "IdComuna"]:
        detail[col] = to_int_series(detail[col])
    detail["IdEstablecimiento"] = code_text(detail["IdEstablecimiento"])
    detail["CodigoPrestacion"] = code_text(detail["CodigoPrestacion"])
    for col in [f"Col{i:02d}" for i in range(1, 21)]:
        detail[col] = to_int_series(detail[col])

    detail = merge_master(detail, master)
    return detail


# ─────────────────────────────────────────────
# 4. DENOMINADOR POBLACIONAL (FONASA)
# ─────────────────────────────────────────────

DENOMINATOR_CODE_ALIASES = {"311001": "201674"}

AGE_GROUPS_CV = {
    "15_19": (15, 19),
    "20_24": (20, 24),
    "25_29": (25, 29),
    "30_34": (30, 34),
    "35_39": (35, 39),
    "40_44": (40, 44),
    "45_49": (45, 49),
    "50_54": (50, 54),
    "55_59": (55, 59),
    "60_64": (60, 64),
    "65_69": (65, 69),
    "70_74": (70, 74),
    "75_79": (75, 79),
    "80_mas": (80, 120),
}

AGE_COLS_CV = list(AGE_GROUPS_CV.keys())
SEX_COLS_CV = ["hombres", "mujeres"]


def load_denominador_fonasa(poblacion_config: dict) -> pd.DataFrame:
    source = poblacion_config["fuente_fonasa"]["2025"]
    path = Path(source["path"])
    sheet = source["sheets"][0]

    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header_row = None
    for idx in range(len(raw)):
        vals = [str(v).strip() for v in raw.iloc[idx].tolist() if pd.notna(v)]
        if len(vals) >= 5 and any(t in v.lower() for v in vals for t in ["codigo", "servicio", "centro"]):
            header_row = idx
            break
    if header_row is None:
        raise ValueError("No se encontro fila de encabezado en FONASA.")

    header = raw.iloc[header_row].tolist()
    df = raw.iloc[header_row + 1:].copy()
    df.columns = header

    filtros = poblacion_config["filtros_poblacion"]
    df = df.rename(columns={
        "Servicio de Salud": "servicio_salud_den",
        "Dependencia": "dependencia_den",
        "Comuna": "comuna_den",
        "C\u00f3digo Centro": "IdEstablecimiento",
        "Nombre Centro": "establecimiento_den",
        "Sexo": "sexo",
        "Edad": "edad",
        "Inscritos": "inscritos",
    })
    df["IdEstablecimiento"] = code_text(df["IdEstablecimiento"])
    df["IdEstablecimiento"] = df["IdEstablecimiento"].replace(DENOMINATOR_CODE_ALIASES)
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    df["inscritos"] = to_int_series(df["inscritos"])
    df["sexo"] = df["sexo"].astype(str).str.strip()
    df["comuna_den"] = df["comuna_den"].astype(str).str.strip()
    df["establecimiento_den"] = df["establecimiento_den"].astype(str).str.strip()

    df = df[df["edad"] >= 15].copy()
    df = df[df["sexo"].isin(["Hombres", "Mujeres"])].copy()

    def assign_group(age):
        for gname, (lo, hi) in AGE_GROUPS_CV.items():
            if lo <= age <= hi:
                return gname
        return None

    df["grupo_etario"] = df["edad"].apply(assign_group)
    df = df[df["grupo_etario"].notna()].copy()
    return df


def build_denominador_establecimiento(detail: pd.DataFrame, master: pd.DataFrame) -> pd.DataFrame:
    geo_cols = ["IdEstablecimiento", "servicio_salud_den", "comuna_den", "establecimiento_den"]
    for col in geo_cols:
        if detail[col].isna().any():
            detail[col] = detail[col].fillna("Sin_dato")

    pivot = detail.pivot_table(
        index=geo_cols,
        columns="grupo_etario",
        values="inscritos",
        aggfunc="sum",
        fill_value=0,
    ).reset_index().rename_axis(None, axis=1)

    for col in AGE_COLS_CV:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot["total_15_mas"] = pivot[AGE_COLS_CV].sum(axis=1)
    out = merge_master(pivot, master, id_col="IdEstablecimiento")

    out = out.rename(columns={
        "servicio_salud_den": "servicio_salud_denominador",
        "comuna_den": "comuna_denominador",
        "establecimiento_den": "establecimiento_denominador",
    })
    return out


# ─────────────────────────────────────────────
# 5. CALCULO DE INDICADORES
# ─────────────────────────────────────────────


def geo_columns(level: str) -> list[str]:
    if level == "establecimiento":
        return [
            "Ano", "IdServicio_master", "servicio_salud_master",
            "IdComuna_master", "comuna_master",
            "IdEstablecimiento", "establecimiento_master",
            "tipo_establecimiento_master", "dependencia_master",
        ]
    if level == "comuna":
        return ["Ano", "IdServicio_master", "servicio_salud_master", "IdComuna_master", "comuna_master"]
    if level == "servicio_salud":
        return ["Ano", "IdServicio_master", "servicio_salud_master"]
    if level == "rm":
        return ["Ano"]
    raise ValueError(f"Nivel no soportado: {level}")


def str_cols_for_groupby(df: pd.DataFrame, cols: list[str]) -> list[str]:
    result = []
    for c in cols:
        if c in df.columns:
            if df[c].dtype == "object":
                df[c] = df[c].fillna("Sin_dato").astype(str)
            result.append(c)
    return result


def sum_by_level(df: pd.DataFrame, level: str, value_cols: list[str]) -> pd.DataFrame:
    cols = geo_columns(level)
    group_cols = str_cols_for_groupby(df, cols)
    existing_val = [c for c in value_cols if c in df.columns]
    out = df.groupby(group_cols, dropna=False, as_index=False)[existing_val].sum(numeric_only=True)
    out.insert(1, "nivel_geografico", level)
    return out


def calcular_todos_los_indicadores(
    numerador_p4: pd.DataFrame,
    denominador_pob: pd.DataFrame,
    prevalencia_hta: float,
    prevalencia_dm2: float,
) -> dict[str, pd.DataFrame]:
    num = numerador_p4[numerador_p4["es_aps"].eq(True)].copy()
    den = denominador_pob[denominador_pob["es_aps"].eq(True)].copy()

    geo_cols = [
        "IdServicio_master", "servicio_salud_master",
        "IdComuna_master", "comuna_master", "establecimiento_master",
        "tipo_establecimiento_master", "dependencia_master",
    ]
    idx_cols = ["Ano", "IdEstablecimiento"]

    p4 = num.pivot_table(
        index=idx_cols,
        columns="CodigoPrestacion",
        values="Col01",
        aggfunc="sum",
        fill_value=0,
    ).reset_index().rename_axis(None, axis=1)

    num_geo = num[idx_cols + geo_cols].drop_duplicates(subset=idx_cols)
    merged_geo = p4.merge(num_geo, on=idx_cols, how="left")

    col_map = {c: f"{c}_den" for c in AGE_COLS_CV + ["total_15_mas"]}
    den_pob_agg = den.groupby("IdEstablecimiento", as_index=False)[AGE_COLS_CV + ["total_15_mas"]].sum()
    den_pob_agg = den_pob_agg.rename(columns=col_map)
    combined = merged_geo.merge(den_pob_agg, on="IdEstablecimiento", how="left")

    def safe_get(df, code, default=0):
        return df[code] if code in df.columns else default

    combined["pob_hta_estimada"] = combined["total_15_mas_den"] * prevalencia_hta / 100
    combined["pob_dm2_estimada"] = combined["total_15_mas_den"] * prevalencia_dm2 / 100

    combined["ind_01_num"] = safe_get(combined, "P4150601")
    combined["ind_01_den"] = combined["pob_hta_estimada"]
    combined["ind_01_pct"] = (combined["ind_01_num"] / combined["ind_01_den"] * 100).where(combined["ind_01_den"].gt(0))

    combined["ind_02_num"] = safe_get(combined, "P4180200") + safe_get(combined, "P4200100")
    combined["ind_02_den"] = safe_get(combined, "P4150601")
    combined["ind_02_pct"] = (combined["ind_02_num"] / combined["ind_02_den"] * 100).where(combined["ind_02_den"].gt(0))

    combined["ind_03_num"] = combined["ind_02_num"]
    combined["ind_03_den"] = combined["pob_hta_estimada"]
    combined["ind_03_pct"] = (combined["ind_03_num"] / combined["ind_03_den"] * 100).where(combined["ind_03_den"].gt(0))

    combined["ind_04_num"] = safe_get(combined, "P4200400")
    combined["ind_04_den"] = safe_get(combined, "P4150601")
    combined["ind_04_pct"] = (combined["ind_04_num"] / combined["ind_04_den"] * 100).where(combined["ind_04_den"].gt(0))

    combined["ind_05_num"] = safe_get(combined, "P4190808")
    combined["ind_05_den"] = safe_get(combined, "P4150601")
    combined["ind_05_pct"] = (combined["ind_05_num"] / combined["ind_05_den"] * 100).where(combined["ind_05_den"].gt(0))

    combined["ind_06_num"] = safe_get(combined, "P4150602")
    combined["ind_06_den"] = combined["pob_dm2_estimada"]
    combined["ind_06_pct"] = (combined["ind_06_num"] / combined["ind_06_den"] * 100).where(combined["ind_06_den"].gt(0))

    combined["ind_07_num"] = safe_get(combined, "P4180300") + safe_get(combined, "P4200200")
    combined["ind_07_den"] = safe_get(combined, "P4150602")
    combined["ind_07_pct"] = (combined["ind_07_num"] / combined["ind_07_den"] * 100).where(combined["ind_07_den"].gt(0))

    combined["ind_08_num"] = combined["ind_07_num"]
    combined["ind_08_den"] = combined["pob_dm2_estimada"]
    combined["ind_08_pct"] = (combined["ind_08_num"] / combined["ind_08_den"] * 100).where(combined["ind_08_den"].gt(0))

    combined["ind_09_num"] = safe_get(combined, "P4190960")
    combined["ind_09_den"] = safe_get(combined, "P4150602")
    combined["ind_09_pct"] = (combined["ind_09_num"] / combined["ind_09_den"] * 100).where(combined["ind_09_den"].gt(0))

    combined["ind_10_num"] = safe_get(combined, "P4200700")
    combined["ind_10_den"] = safe_get(combined, "P4180800")
    combined["ind_10_pct"] = (combined["ind_10_num"] / combined["ind_10_den"] * 100).where(combined["ind_10_den"].gt(0))

    combined["ind_12b_num"] = safe_get(combined, "P4190950")
    combined["ind_12b_den"] = safe_get(combined, "P4150602")
    combined["ind_12b_pct"] = (combined["ind_12b_num"] / combined["ind_12b_den"] * 100).where(combined["ind_12b_den"].gt(0))

    combined["ind_13_num"] = safe_get(combined, "P4301080")
    combined["ind_13_den"] = safe_get(combined, "P4150601")
    combined["ind_13_pct"] = (combined["ind_13_num"] / combined["ind_13_den"] * 100).where(combined["ind_13_den"].gt(0))

    combined["ind_14_num"] = safe_get(combined, "P4301040")
    combined["ind_14_den"] = safe_get(combined, "P4150602")
    combined["ind_14_pct"] = (combined["ind_14_num"] / combined["ind_14_den"] * 100).where(combined["ind_14_den"].gt(0))

    combined["ind_15_num"] = safe_get(combined, "P4200800")
    combined["ind_15_den"] = safe_get(combined, "P4200600")
    combined["ind_15_pct"] = (combined["ind_15_num"] / combined["ind_15_den"] * 100).where(combined["ind_15_den"].gt(0))

    combined["ind_16_ecv"] = safe_get(combined, "P4190900") + safe_get(combined, "P4190910")
    combined["ind_16_num"] = safe_get(combined, "P4190930")
    combined["ind_16_den"] = combined["ind_16_ecv"]
    combined["ind_16_pct"] = (combined["ind_16_num"] / combined["ind_16_den"] * 100).where(combined["ind_16_den"].gt(0))

    combined["ind_17_num"] = safe_get(combined, "P4190940")
    combined["ind_17_den"] = combined["ind_16_ecv"]
    combined["ind_17_pct"] = (combined["ind_17_num"] / combined["ind_17_den"] * 100).where(combined["ind_17_den"].gt(0))

    outputs = {"detalle_establecimiento": combined}
    return outputs


# ─────────────────────────────────────────────
# 6. AGRUPACION POR NIVEL GEOGRAFICO
# ─────────────────────────────────────────────

INDICADORES_META = [
    ("ind_01", "Cobertura HTA"),
    ("ind_02", "Control HTA"),
    ("ind_03", "Cobertura efectiva HTA"),
    ("ind_04", "HTA muy descompensadas"),
    ("ind_05", "Indice Madurez HEARTS"),
    ("ind_06", "Cobertura DM2"),
    ("ind_07", "Control DM2"),
    ("ind_08", "Cobertura efectiva DM2"),
    ("ind_09", "DM2 muy descompensadas"),
    ("ind_10", "DM2 compensada usuarias insulina"),
    ("ind_12b", "DM2 fondo de ojo vigente"),
    ("ind_13", "HTA evaluacion funcion renal"),
    ("ind_14", "DM2 evaluacion funcion renal"),
    ("ind_15", "DM+ERC tratamiento IECA/ARA II"),
    ("ind_16", "ECV antiagregante plaquetario"),
    ("ind_17", "ECV estatinas"),
]


def agregar_por_nivel(
    detalle: pd.DataFrame, niveles: list[str]
) -> dict[str, dict[str, pd.DataFrame]]:
    resultados = {}
    for nivel in niveles:
        nivel_out = {}
        for ind_id, ind_nombre in INDICADORES_META:
            num_col = f"{ind_id}_num"
            den_col = f"{ind_id}_den"
            pct_col = f"{ind_id}_pct"

            if num_col not in detalle.columns:
                continue

            agg = sum_by_level(detalle, nivel, [num_col, den_col])
            agg[pct_col] = (agg[num_col] / agg[den_col] * 100).where(agg[den_col].gt(0))
            agg["indicador_id"] = ind_id
            agg["indicador_nombre"] = ind_nombre
            nivel_out[ind_id] = agg
        resultados[nivel] = nivel_out
    return resultados


def escribir_resultados(
    detalle: pd.DataFrame,
    agregados: dict[str, dict[str, pd.DataFrame]],
    denominador_pob: pd.DataFrame,
    numerador_p4_raw: pd.DataFrame,
    numerador_a05: pd.DataFrame | None,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    detalle.to_csv(OUTPUT_DIR / "detalle_indicadores_establecimiento.csv", index=False, encoding="utf-8-sig")
    print(f"Escrito: {OUTPUT_DIR / 'detalle_indicadores_establecimiento.csv'}")

    consolidado_rows = []
    for nivel, indicadores in agregados.items():
        for ind_id, df in indicadores.items():
            path = OUTPUT_DIR / f"indicador_{ind_id}_{nivel}.csv"
            df.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"Escrito: {path}")
            consolidado_rows.append(df)

    if consolidado_rows:
        consolidado = pd.concat(consolidado_rows, ignore_index=True)
        consolidado.to_csv(OUTPUT_DIR / "consolidado_indicadores_cardiovasculares.csv", index=False, encoding="utf-8-sig")
        print(f"Escrito: {OUTPUT_DIR / 'consolidado_indicadores_cardiovasculares.csv'}")

    denominador_pob.to_csv(OUTPUT_DIR / "denominador_poblacion_inscrita.csv", index=False, encoding="utf-8-sig")
    print(f"Escrito: {OUTPUT_DIR / 'denominador_poblacion_inscrita.csv'}")

    p4_export = numerador_p4_raw.drop_duplicates()
    p4_export.to_csv(OUTPUT_DIR / "numerador_p4_filtrado.csv", index=False, encoding="utf-8-sig")
    print(f"Escrito: {OUTPUT_DIR / 'numerador_p4_filtrado.csv'}")

    if numerador_a05 is not None and not numerador_a05.empty:
        a05_export = numerador_a05.drop_duplicates()
        a05_export.to_csv(OUTPUT_DIR / "numerador_a05_pscv_filtrado.csv", index=False, encoding="utf-8-sig")
        print(f"Escrito: {OUTPUT_DIR / 'numerador_a05_pscv_filtrado.csv'}")


def imprimir_resumen_rm(agregados: dict[str, dict[str, pd.DataFrame]]) -> None:
    if "rm" not in agregados:
        return
    rm_indicadores = agregados["rm"]
    ind_orden = [x[0] for x in INDICADORES_META]
    print("\n=== RESUMEN RM ===")
    print(f"{'Indicador':<45} {'N':>10} {'D':>10} {'%':>8}")
    print("-" * 75)
    for ind_id in ind_orden:
        if ind_id not in rm_indicadores:
            continue
        df = rm_indicadores[ind_id]
        num_col = f"{ind_id}_num"
        den_col = f"{ind_id}_den"
        pct_col = f"{ind_id}_pct"
        for _, row in df.iterrows():
            nombre = row.get("indicador_nombre", ind_id)
            n = int(row[num_col]) if pd.notna(row.get(num_col)) else 0
            d = int(row[den_col]) if pd.notna(row.get(den_col)) else 0
            p = row.get(pct_col)
            p_str = f"{p:.2f}%" if pd.notna(p) else "N/D"
            print(f"{nombre:<45} {n:>10,} {d:>10,} {p_str:>8}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────


def main() -> None:
    config = load_config()
    pob_config = load_poblacion_config()
    prevalencia_hta = pob_config["prevalencias_poblacionales"]["hta"]["prevalencia_pct"]
    prevalencia_dm2 = pob_config["prevalencias_poblacionales"]["dm2"]["prevalencia_pct"]

    print("Cargando maestro de establecimientos...")
    master = build_master_lookup(Path(config["input_paths"]["maestro_establecimientos"]))

    print("Extrayendo numerador desde Serie P (REM P4)...")
    numerador_p4 = extract_numerador_p4(config, master)
    print(f"  Registros P4 cargados: {len(numerador_p4):,}")

    print("Extrayendo numerador desde Serie A (REM A05 Secciones H/I)...")
    try:
        numerador_a05 = extract_numerador_a05(config, master)
        if not numerador_a05.empty:
            print(f"  Registros A05 cargados: {len(numerador_a05):,}")
        else:
            print("  Sin registros A05 para PSCV.")
            numerador_a05 = None
    except Exception as e:
        print(f"  AVISO: {e}")
        numerador_a05 = None

    print("Cargando denominador poblacional desde FONASA...")
    denom_raw = load_denominador_fonasa(pob_config)
    print(f"  Registros FONASA 15+: {len(denom_raw):,}")
    denominador_pob = build_denominador_establecimiento(denom_raw, master)
    print(f"  Establecimientos con denominador: {len(denominador_pob):,}")

    print("Calculando indicadores...")
    outputs = calcular_todos_los_indicadores(numerador_p4, denominador_pob, prevalencia_hta, prevalencia_dm2)
    detalle = outputs["detalle_establecimiento"]

    niveles = ["establecimiento", "comuna", "servicio_salud", "rm"]
    agregados = agregar_por_nivel(detalle, niveles)

    print("Escribiendo resultados...")
    escribir_resultados(detalle, agregados, denominador_pob, numerador_p4, numerador_a05)

    imprimir_resumen_rm(agregados)

    print("\n=== COMPLETADO ===")
    print(f"Todos los archivos fueron guardados en: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
