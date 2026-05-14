from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "2025"

DASHBOARD_DATA_PATH = DATA_DIR / "indicadores_cardiovascular_dashboard_2024_2025.csv"
PANEL_PATH = DATA_DIR / "indicadores_cardiovascular_panel_2026.csv"
VALIDACION_PATH = DATA_DIR / "indicadores_cardiovascular_validacion_rm_2024.csv"
ORIGENES_PATH = DATA_DIR / "indicadores_cardiovascular_2026_origenes_y_codigos.csv"
EGRESOS_PATH = DATA_DIR / "indicadores_egresos_rm_2024_2025.csv"

LEVEL_LABELS = {
    "rm": "Región Metropolitana",
    "servicio_salud": "Servicio de salud",
    "comuna": "Comuna",
    "establecimiento": "Establecimiento",
}

EGRESOS_LEVEL_LABELS = {
    "rm": "Región Metropolitana",
    "servicio_salud": "Servicio de salud",
    "comuna": "Comuna",
}
GROUP_ORDER = [
    "HTA y HEARTS",
    "DM2 y seguimiento",
    "Función renal y ERC",
    "ECV y prevención secundaria",
    "Egresos hospitalarios",
]
PENDING_INDICATORS = ["5", "12a"]


def _locale_decimal(value: float, decimals: int = 2) -> str:
    sign = "-" if value < 0 else ""
    formatted = f"{abs(value):.{decimals}f}"
    int_part, dec_part = formatted.split(".")
    int_part = f"{int(int_part):,}".replace(",", ".")
    return f"{sign}{int_part},{dec_part}"


def format_int(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if pd.isna(numeric):
        return ""
    return f"{int(round(numeric)):,}".replace(",", ".")


def format_pp(value: object, digits: int = 3) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if pd.isna(numeric):
        return ""
    sign = "+" if numeric > 0 else ""
    return f"{sign}{_locale_decimal(numeric, digits)} pp"


def indicator_sort_key(indicator_id: object) -> tuple[int, int, str]:
    text = str(indicator_id).strip()
    digits = "".join(char for char in text if char.isdigit())
    suffix = text[len(digits) :].lower() if digits else text.lower()
    suffix_rank = {"a": 0, "b": 1}.get(suffix, 9)
    return (int(digits or 999), suffix_rank, text)


def indicator_label(indicator_id: object, indicator_name: object) -> str:
    return f"{str(indicator_id).strip()}. {str(indicator_name).strip()}"


def format_indicator_value(raw_value: object, unidad: str = "%") -> str:
    numeric = pd.to_numeric(raw_value, errors="coerce")
    if pd.isna(numeric):
        return ""
    if unidad == "por 10.000":
        return _locale_decimal(float(numeric), 1)
    return _locale_decimal(float(numeric), 2) + "%"


def clean_multiline(text: object) -> str:
    clean = str(text or "").strip()
    if clean.lower() == "nan":
        return ""
    return clean


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


@st.cache_data(show_spinner=False)
def load_dashboard_data() -> pd.DataFrame:
    if not DASHBOARD_DATA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {DASHBOARD_DATA_PATH}")

    df = pd.read_csv(DASHBOARD_DATA_PATH, dtype={"indicador_id": str})
    numeric_columns = [
        "Ano",
        "numerador",
        "denominador",
        "establecimientos_reportantes",
        "establecimientos_con_denominador",
        "valor",
        "valor_orden",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["indicador_id"] = df["indicador_id"].astype(str).str.strip()
    df["es_aps_bool"] = df["es_aps"].astype(str).str.strip().str.lower().eq("true")
    return df


@st.cache_data(show_spinner=False)
def load_panel_reference() -> pd.DataFrame:
    if not PANEL_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {PANEL_PATH}")

    df = pd.read_csv(PANEL_PATH, dtype={"indicador_id": str}).fillna("")
    df["indicador_id"] = df["indicador_id"].astype(str).str.strip()
    df["orden_num"] = pd.to_numeric(df["orden"], errors="coerce")
    numeric_columns = ["amplificador"]
    for column in numeric_columns:
        df[f"{column}_num"] = pd.to_numeric(df[column], errors="coerce")
    df["unidad_calculo"] = df["amplificador_num"].map(lambda value: "por 10.000" if pd.notna(value) and float(value) >= 10000 else "%")
    return df.sort_values("orden_num").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_validation() -> pd.DataFrame:
    if not VALIDACION_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(VALIDACION_PATH, dtype={"indicador_id": str}).fillna("")
    numeric_columns = [
        "Ano",
        "numerador",
        "denominador",
        "valor_calculado_pct",
        "valor_referencia_2024_rm_proporcion",
        "diferencia_pp",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["indicador_id"] = df["indicador_id"].astype(str).str.strip()
    return df.sort_values(by="indicador_id", key=lambda col: col.map(indicator_sort_key)).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_indicator_sources() -> pd.DataFrame:
    if not ORIGENES_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(ORIGENES_PATH, dtype=str).fillna("")
    df["indicador"] = df["indicador"].astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False)
def load_egresos_data() -> pd.DataFrame:
    if not EGRESOS_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(EGRESOS_PATH, dtype={"indicador_id": str})
    df["indicador_id"] = df["indicador_id"].astype(str).str.strip()
    numeric_columns = ["Ano", "n_egresos", "denominador_piv", "tasa_x10000"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def available_years(data: pd.DataFrame) -> list[int]:
    return sorted(data["Ano"].dropna().astype(int).unique().tolist(), reverse=True)


def service_options(data: pd.DataFrame, year: int) -> list[str]:
    rows = data[data["Ano"] == year]
    return sorted(rows["servicio_salud"].dropna().astype(str).unique().tolist())


def comuna_options(data: pd.DataFrame, year: int, service_name: str | None = None) -> list[str]:
    rows = data[(data["Ano"] == year) & data["comuna"].notna()].copy()
    rows = rows[rows["comuna"].astype(str).str.strip() != ""]
    if service_name:
        rows = rows[rows["servicio_salud"] == service_name]
    return sorted(rows["comuna"].astype(str).unique().tolist())


def establishment_options(
    data: pd.DataFrame,
    year: int,
    service_name: str | None = None,
    comuna_name: str | None = None,
    only_aps: bool = True,
) -> list[str]:
    rows = data[(data["Ano"] == year) & data["establecimiento"].notna()].copy()
    rows = rows[rows["establecimiento"].astype(str).str.strip() != ""]
    if service_name:
        rows = rows[rows["servicio_salud"] == service_name]
    if comuna_name:
        rows = rows[rows["comuna"] == comuna_name]
    if only_aps:
        rows = rows[rows["es_aps_bool"]]
    return sorted(rows["establecimiento"].astype(str).unique().tolist())


def get_territory_label(
    level: str,
    service_name: str | None = None,
    comuna_name: str | None = None,
    establishment_name: str | None = None,
) -> str:
    if level == "rm":
        return "Región Metropolitana"
    if level == "servicio_salud":
        return service_name or "Servicio de salud"
    if level == "comuna":
        return comuna_name or "Comuna"
    return establishment_name or "Establecimiento"


def get_selected_territory_rows(
    data: pd.DataFrame,
    year: int,
    level: str,
    service_name: str | None = None,
    comuna_name: str | None = None,
    establishment_name: str | None = None,
) -> pd.DataFrame:
    rows = data[(data["Ano"] == year) & (data["nivel"] == level)].copy()
    if level == "servicio_salud" and service_name:
        rows = rows[rows["servicio_salud"] == service_name]
    if level == "comuna":
        if service_name:
            rows = rows[rows["servicio_salud"] == service_name]
        if comuna_name:
            rows = rows[rows["comuna"] == comuna_name]
    if level == "establecimiento":
        if service_name:
            rows = rows[rows["servicio_salud"] == service_name]
        if comuna_name:
            rows = rows[rows["comuna"] == comuna_name]
        if establishment_name:
            rows = rows[rows["establecimiento"] == establishment_name]
    return rows.reset_index(drop=True)


def filter_panel_by_group(panel: pd.DataFrame, group_name: str) -> pd.DataFrame:
    if group_name == "Todos":
        return panel
    return panel[panel["grupo_indicador"] == group_name].copy()


def build_excel_like_table(
    panel: pd.DataFrame,
    selected_rows: pd.DataFrame,
    selected_year: int,
    territory_label: str,
    show_definitions: bool,
    only_available: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    calc = selected_rows[["indicador_id", "valor", "numerador", "denominador", "estado_calculo", "metodo_calculo"]].copy()
    calc = calc.rename(
        columns={
            "valor": "valor_calculado",
            "numerador": "numerador_calculado",
            "denominador": "denominador_calculado",
            "estado_calculo": "estado_calculado",
            "metodo_calculo": "metodo_calculado",
        }
    )

    table = panel.merge(calc, on="indicador_id", how="left")

    if only_available:
        has_reference = table["valor_2024_rm_num"].notna() | table["valor_2025_num"].notna()
        has_calc = pd.to_numeric(table["valor_calculado"], errors="coerce").notna()
        table = table[has_reference | has_calc].copy()

    calc_header = f"{selected_year} seleccionado"

    display = pd.DataFrame()
    display["Indicador"] = table["indicador_id"]
    display["Nombre del indicador"] = table["nombre_indicador"]
    if show_definitions:
        display["Numerador"] = table["numerador"].map(clean_multiline)
        display["Denominador"] = table["denominador"].map(clean_multiline)
    display["Unidad"] = table["unidad_calculo"]
    display[calc_header] = table.apply(
        lambda row: format_indicator_value(row["valor_calculado"], row["unidad_calculo"]),
        axis=1,
    )
    display["N"] = table["numerador_calculado"].map(format_int)
    display["D"] = table["denominador_calculado"].map(format_int)
    display["Estado"] = table["estado_calculado"].replace({"calculado": "Calculado", "proxy": "Proxy"}).fillna("")
    display["Disponibilidad"] = table["estado_local"]
    display["Método"] = table["metodo_calculado"].fillna("")

    download = table[
        [
            "indicador_id",
            "nombre_indicador",
            "numerador",
            "denominador",
            "unidad_calculo",
            "valor_calculado",
            "numerador_calculado",
            "denominador_calculado",
            "estado_calculado",
            "estado_local",
            "metodo_calculado",
        ]
    ].rename(
        columns={
            "indicador_id": "Indicador",
            "nombre_indicador": "Nombre del indicador",
            "numerador": "Numerador",
            "denominador": "Denominador",
            "unidad_calculo": "Unidad",
            "valor_calculado": calc_header,
            "numerador_calculado": "N",
            "denominador_calculado": "D",
            "estado_calculado": "Estado",
            "estado_local": "Disponibilidad",
            "metodo_calculado": "Método",
        }
    )
    download.insert(0, "Territorio", territory_label)
    download.insert(0, "Nivel", "")
    download.insert(0, "Año seleccionado", selected_year)

    return display.reset_index(drop=True), download.reset_index(drop=True)


def build_validation_display(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    work = df.copy()
    work["Indicador"] = work.apply(
        lambda row: indicator_label(row["indicador_id"], row["nombre_indicador"]),
        axis=1,
    )
    work["Estado"] = work["estado_calculo"].replace({"proxy": "Proxy", "calculado": "Calculado"})
    work["Valor calculado RM 2024"] = work["valor_calculado_pct"].map(lambda value: format_indicator_value(value))
    work["Valor planilla RM 2024"] = work["valor_referencia_2024_rm_proporcion"].map(
        lambda value: format_indicator_value(pd.to_numeric(value, errors="coerce") * 100)
    )
    work["Brecha"] = work["diferencia_pp"].map(lambda value: format_pp(value, 3))
    return work[
        [
            "Indicador",
            "Estado",
            "Valor calculado RM 2024",
            "Valor planilla RM 2024",
            "Brecha",
        ]
    ]


def build_level_matrix(
    data: pd.DataFrame,
    panel: pd.DataFrame,
    level: str,
    only_aps: bool = False,
) -> pd.DataFrame:
    subset = data[data["nivel"] == level].copy()
    subset = subset[subset["Ano"].isin([2024, 2025])].copy()
    if level == "establecimiento" and only_aps:
        subset = subset[subset["es_aps_bool"]]

    indicator_ids = (
        panel[panel["estado_local"].isin(["Exacto", "Exacto solo 2025"])]["indicador_id"]
        .astype(str)
        .tolist()
    )
    subset = subset[subset["indicador_id"].isin(indicator_ids)].copy()

    if level == "rm":
        id_cols = []
        subset["Territorio"] = "Región Metropolitana"
        base_cols = ["Territorio"]
    elif level == "servicio_salud":
        id_cols = ["servicio_salud"]
        base_cols = ["Servicio de salud"]
        subset["Servicio de salud"] = subset["servicio_salud"]
    elif level == "comuna":
        id_cols = ["servicio_salud", "comuna"]
        base_cols = ["Servicio de salud", "Comuna"]
        subset["Servicio de salud"] = subset["servicio_salud"]
        subset["Comuna"] = subset["comuna"]
    else:
        id_cols = ["servicio_salud", "comuna", "establecimiento"]
        base_cols = ["Servicio de salud", "Comuna", "Establecimiento"]
        subset["Servicio de salud"] = subset["servicio_salud"]
        subset["Comuna"] = subset["comuna"]
        subset["Establecimiento"] = subset["establecimiento"]

    subset["columna_indicador"] = subset["indicador_id"] + " (" + subset["Ano"].astype(int).astype(str) + ")"
    pivot = subset.pivot_table(
        index=base_cols,
        columns="columna_indicador",
        values="valor",
        aggfunc="first",
    ).reset_index()

    ordered_indicator_cols: list[str] = []
    available_cols = set(pivot.columns.tolist())
    for indicator_id in indicator_ids:
        for year in [2024, 2025]:
            candidate = f"{indicator_id} ({year})"
            if candidate in available_cols:
                ordered_indicator_cols.append(candidate)

    pivot = pivot[base_cols + ordered_indicator_cols].copy()
    for col in ordered_indicator_cols:
        pivot[col] = pivot[col].map(lambda value: format_indicator_value(value))

    return pivot.sort_values(base_cols).reset_index(drop=True)


def build_indicator_dictionary(panel: pd.DataFrame) -> pd.DataFrame:
    dictionary = panel.copy()
    dictionary["Indicador"] = dictionary["indicador_id"]
    dictionary["Nombre"] = dictionary["nombre_indicador"]
    dictionary["Unidad"] = dictionary["unidad_calculo"]
    dictionary["Disponibilidad"] = dictionary["estado_local"]
    dictionary["Numerador"] = dictionary["numerador"].map(clean_multiline)
    dictionary["Denominador"] = dictionary["denominador"].map(clean_multiline)
    return dictionary[["Indicador", "Nombre", "Unidad", "Disponibilidad", "Numerador", "Denominador"]]


def build_indicator_options(panel: pd.DataFrame) -> list[str]:
    available = panel[panel["estado_local"].isin(["Exacto", "Exacto solo 2025"])]["indicador_id"].astype(str).tolist()
    return sorted(available, key=indicator_sort_key)


def build_indicator_name_lookup(panel: pd.DataFrame) -> dict[str, str]:
    return panel.set_index("indicador_id")["nombre_indicador"].to_dict()


def build_single_indicator_table(
    data: pd.DataFrame,
    level: str,
    indicator_id: str,
    only_aps: bool = False,
) -> pd.DataFrame:
    subset = data[(data["nivel"] == level) & (data["indicador_id"] == indicator_id)].copy()
    subset = subset[subset["Ano"].isin([2024, 2025])].copy()
    if level == "establecimiento" and only_aps:
        subset = subset[subset["es_aps_bool"]]

    if level == "rm":
        subset["Región"] = "Región Metropolitana"
        id_cols = ["Región"]
    elif level == "servicio_salud":
        subset["Servicio de salud"] = subset["servicio_salud"]
        id_cols = ["Servicio de salud"]
    elif level == "comuna":
        subset["Servicio de salud"] = subset["servicio_salud"]
        subset["Comuna"] = subset["comuna"]
        id_cols = ["Servicio de salud", "Comuna"]
    else:
        subset["Servicio de salud"] = subset["servicio_salud"]
        subset["Comuna"] = subset["comuna"]
        subset["Establecimiento"] = subset["establecimiento"]
        id_cols = ["Servicio de salud", "Comuna", "Establecimiento"]

    wide = subset.pivot_table(
        index=id_cols,
        columns="Ano",
        values=["valor", "numerador", "denominador", "estado_calculo"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{year}" for metric, year in wide.columns]
    wide = wide.reset_index()

    for year in [2024, 2025]:
        value_col = f"valor_{year}"
        numerator_col = f"numerador_{year}"
        denominator_col = f"denominador_{year}"
        state_col = f"estado_calculo_{year}"
        if value_col in wide.columns:
            wide[f"{year}"] = wide[value_col].map(format_indicator_value)
        else:
            wide[f"{year}"] = ""
        if numerator_col in wide.columns:
            wide[f"N {year}"] = wide[numerator_col].map(format_int)
        else:
            wide[f"N {year}"] = ""
        if denominator_col in wide.columns:
            wide[f"D {year}"] = wide[denominator_col].map(format_int)
        else:
            wide[f"D {year}"] = ""
        if state_col in wide.columns:
            wide[f"Estado {year}"] = wide[state_col].replace({"calculado": "Calculado", "proxy": "Proxy"}).fillna("")
        else:
            wide[f"Estado {year}"] = ""

    ordered_cols = id_cols + ["2024", "N 2024", "D 2024", "Estado 2024", "2025", "N 2025", "D 2025", "Estado 2025"]
    return wide[ordered_cols].sort_values(id_cols).reset_index(drop=True)


SHORT_NUM: dict[str, str] = {
    "1": "REM-P4: Personas bajo control HTA",
    "2": "REM-P4: PA < 140/90 + < 150/90 mmHg",
    "3": "REM-P4: PA < 140/90 + < 150/90 mmHg",
    "4": "REM-P4: PA ≥ 160/100 mmHg",
    "5": "Índice Madurez HEARTS",
    "6": "REM-P4: Personas bajo control DM2",
    "7": "REM-P4: HbA1c < 7% (15-79) + < 9% (80+)",
    "8": "REM-P4: HbA1c < 7% (15-79) + < 9% (80+)",
    "9": "REM-P4: HbA1c ≥ 9%",
    "10": "REM-P4: DM2 compensada + insulina",
    "11": "REM-P4: Evaluación pie diabético vigente",
    "12a": "REM-P4: Tamizaje RD vigente",
    "12b": "REM-P4: Fondo de ojo vigente",
    "13": "REM-P4: Con VFGe y RAC en HTA",
    "14": "REM-P4: Con VFGe y RAC en DM2",
    "15": "REM-P4: DM+ERC con IECA o ARA II",
    "16": "REM-P4: ECV con antiagregante plaquetario",
    "17": "REM-P4: ECV con estatinas",
    "18": "EGRESOS: CIE-10 G45, I63-I69",
    "19": "EGRESOS: CIE-10 I20-I25",
    "20": "EGRESOS: CIE-10 I50, J81",
    "21": "EGRESOS: CIE-10 E11-E14",
    "22": "EGRESOS: DM + PROCED 1701 (amputación)",
}

SHORT_DEN: dict[str, str] = {
    "1": "FONASA: PIV 15+ × 27.6% HTA",
    "2": "REM-P4: Personas bajo control HTA",
    "3": "FONASA: PIV 15+ × 27.6% HTA",
    "4": "REM-P4: Personas bajo control HTA",
    "5": "Fuente externa HEARTS",
    "6": "FONASA: PIV 15+ × 12.3% DM2",
    "7": "REM-P4: Personas bajo control DM2",
    "8": "FONASA: PIV 15+ × 12.3% DM2",
    "9": "REM-P4: Personas bajo control DM2",
    "10": "REM-P4: Personas DM2 usuarias insulina",
    "11": "REM-P4: Personas bajo control DM2",
    "12a": "REM-P4: Personas DM2 sin RD",
    "12b": "REM-P4: Personas bajo control DM2",
    "13": "REM-P4: Personas bajo control HTA",
    "14": "REM-P4: Personas bajo control DM2",
    "15": "REM-P4: Personas DM+ERC",
    "16": "REM-P4: Personas bajo control ECV",
    "17": "REM-P4: Personas bajo control ECV",
    "18": "FONASA: Población FONASA 15+",
    "19": "FONASA: Población FONASA 15+",
    "20": "FONASA: Población FONASA 15+",
    "21": "FONASA: Población FONASA 15+",
    "22": "FONASA: Población FONASA 15+",
}

EGRESOS_NAMES: dict[str, str] = {
    "18": "Tasa egresos enfermedad cerebrovascular",
    "19": "Tasa egresos enf. isquémicas corazón",
    "20": "Tasa egresos insuficiencia cardíaca",
    "21": "Tasa egresos diabetes mellitus",
    "22": "Tasa egresos amputación pie diabético",
}


def render_excel_like_page() -> None:
    data = load_dashboard_data()
    egresos = load_egresos_data()

    st.title("Indicadores cardiovasculares RM")
    st.caption(
        "Indicadores calculados para la Región Metropolitana desde fuentes REM, FONASA y DEIS."
    )

    rem_ids = sorted(data["indicador_id"].unique(), key=indicator_sort_key)
    names = (
        data[["indicador_id", "nombre_indicador"]]
        .drop_duplicates("indicador_id")
        .set_index("indicador_id")["nombre_indicador"]
        .to_dict()
    )
    names_2025 = (
        data[data["Ano"] == 2025][["indicador_id", "nombre_indicador"]]
        .drop_duplicates("indicador_id")
        .set_index("indicador_id")["nombre_indicador"]
        .to_dict()
    )
    names.update(names_2025)
    names.update(EGRESOS_NAMES)

    rm_2024_vals = data[(data["nivel"] == "rm") & (data["Ano"] == 2024)].set_index("indicador_id")["valor"]
    rm_2025_vals = data[(data["nivel"] == "rm") & (data["Ano"] == 2025)].set_index("indicador_id")["valor"]

    rm_2024_unidad = data[(data["nivel"] == "rm") & (data["Ano"] == 2024)].set_index("indicador_id")["unidad"].to_dict()
    rm_2025_unidad = data[(data["nivel"] == "rm") & (data["Ano"] == 2025)].set_index("indicador_id")["unidad"].to_dict()

    if not egresos.empty:
        eg_2024 = egresos[(egresos["nivel"] == "rm") & (egresos["Ano"] == 2024)].set_index("indicador_id")["tasa_x10000"]
        eg_2025 = egresos[(egresos["nivel"] == "rm") & (egresos["Ano"] == 2025)].set_index("indicador_id")["tasa_x10000"]

    rows: list[dict[str, str]] = []

    for iid in rem_ids:
        name = names.get(iid, iid)
        rows.append({
            "Indicador": indicator_label(iid, name),
            "Numerador": SHORT_NUM.get(iid, ""),
            "Denominador": SHORT_DEN.get(iid, ""),
            "2024": format_indicator_value(
                rm_2024_vals.get(iid, pd.NA),
                rm_2024_unidad.get(iid, "%"),
            ),
            "2025": format_indicator_value(
                rm_2025_vals.get(iid, pd.NA),
                rm_2025_unidad.get(iid, "%"),
            ),
        })

    if not egresos.empty:
        for iid in ["18", "19", "20", "21", "22"]:
            name = names.get(iid, iid)
            rows.append({
                "Indicador": indicator_label(iid, name),
                "Numerador": SHORT_NUM.get(iid, ""),
                "Denominador": SHORT_DEN.get(iid, ""),
                "2024": format_indicator_value(
                    eg_2024.get(iid, pd.NA) if not egresos.empty else pd.NA,
                    "por 10.000",
                ),
                "2025": format_indicator_value(
                    eg_2025.get(iid, pd.NA) if not egresos.empty else pd.NA,
                    "por 10.000",
                ),
            })

    display = pd.DataFrame(rows)

    st.dataframe(display, use_container_width=True, hide_index=True)
    st.download_button(
        "Descargar resumen RM (CSV)",
        data=csv_bytes(display),
        file_name="resumen_indicadores_rm_2024_2025.csv",
        mime="text/csv",
    )


def render_indicator_table_page() -> None:
    data = load_dashboard_data()
    panel = load_panel_reference()
    indicator_options = build_indicator_options(panel)
    indicator_name_lookup = build_indicator_name_lookup(panel)

    st.title("Tabla por indicador")
    st.caption(
        "Selecciona un indicador y revisa su distribución territorial en formato tabular para `2024` y `2025`."
    )

    control_a, control_b = st.columns([2, 1])
    with control_a:
        default_indicator = "2" if "2" in indicator_options else indicator_options[0]
        indicator_id = st.selectbox(
            "Indicador",
            indicator_options,
            index=indicator_options.index(default_indicator),
            format_func=lambda value: f"{value}. {indicator_name_lookup.get(value, value)}",
        )
    with control_b:
        level = st.selectbox(
            "Nivel",
            ["rm", "servicio_salud", "comuna", "establecimiento"],
            index=1,
            format_func=lambda value: LEVEL_LABELS[value],
        )

    only_aps = False
    if level == "establecimiento":
        only_aps = st.checkbox("Solo APS", value=True)

    table = build_single_indicator_table(data, level, indicator_id, only_aps=only_aps)

    label = indicator_label(indicator_id, indicator_name_lookup.get(indicator_id, indicator_id))
    st.markdown(f"**Indicador:** {label}  \n**Numerador:** {SHORT_NUM.get(indicator_id, '')}  \n**Denominador:** {SHORT_DEN.get(indicator_id, '')}")

    st.caption("**N** = Numerador  |  **D** = Denominador  |  **Estado:** Calculado (directo) · Proxy (aproximación)")
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.info(
        "**Proxy:** los indicadores 16 (antiagregante plaquetario) y 17 (estatinas) usan proxy "
        "en 2024 porque los códigos REM P4 específicos no existían en el diccionario de ese año. "
        "En 2024 se usó el código genérico `P4190930` (ECV antiagregantes) para el indicador 16 "
        "y `P4190940` (ECV estatinas) para el 17. A partir de 2025, el diccionario REM P4 desglosó "
        "estos códigos por condición: `P4401013+P4401016` (IAM+ACV con antiagregantes) y "
        "`P4401014+P4401017` (IAM+ACV con estatinas), que corresponden a la fórmula exacta del indicador."
    )
    st.download_button(
        "Descargar tabla del indicador (CSV)",
        data=csv_bytes(table),
        file_name=f"indicador_{indicator_id}_{level}_2024_2025.csv",
        mime="text/csv",
    )


def render_egresos_page() -> None:
    egresos = load_egresos_data()
    if egresos.empty:
        st.info("No hay datos de egresos disponibles.")
        return

    st.title("Tasas de egresos hospitalarios")
    st.caption(
        "Tasas de egresos hospitalarios calculadas desde DEIS, para población FONASA de 15 años y más, "
        "Región Metropolitana."
    )

    level = st.selectbox(
        "Nivel",
        ["rm", "servicio_salud", "comuna"],
        format_func=lambda value: EGRESOS_LEVEL_LABELS[value],
    )

    servicios = sorted(
        egresos[egresos["nivel"] == "servicio_salud"]["servicio_salud"]
        .dropna().astype(str).unique()
    )
    comunas = sorted(
        egresos[egresos["nivel"] == "comuna"]["comuna"]
        .dropna().astype(str).unique()
    )
    filter_to_ss = None
    filter_to_comuna = None

    if level == "servicio_salud":
        filter_to_ss = st.selectbox("Servicio de salud", servicios)
    elif level == "comuna":
        col_ss, col_com = st.columns(2)
        with col_ss:
            filter_to_ss = st.selectbox("Servicio de salud", [""] + servicios)
        with col_com:
            comuna_options = comunas
            if filter_to_ss:
                ss_ids = egresos[egresos["servicio_salud"] == filter_to_ss]["IdServicio"].iloc[0]
                comuna_options = sorted(
                    egresos[(egresos["nivel"] == "comuna") & (egresos["IdServicio"] == ss_ids)]["comuna"]
                    .dropna().astype(str).unique()
                )
            filter_to_comuna = st.selectbox("Comuna", [""] + comuna_options)

    rows = egresos[egresos["nivel"] == level].copy()
    if level == "servicio_salud" and filter_to_ss:
        rows = rows[rows["servicio_salud"] == filter_to_ss]
    elif level == "comuna":
        if filter_to_ss:
            ss_id = egresos[egresos["servicio_salud"] == filter_to_ss]["IdServicio"].iloc[0]
            rows = rows[rows["IdServicio"] == ss_id]
        if filter_to_comuna:
            rows = rows[rows["comuna"] == filter_to_comuna]

    if rows.empty:
        st.info("No hay datos para la selección actual.")
        return

    names = {
        "18": "Enfermedad cerebrovascular",
        "19": "Enfermedades isquémicas del corazón",
        "20": "Insuficiencia cardíaca",
        "21": "Diabetes mellitus",
        "22": "Amputación extremidad inferior",
    }
    cies = {
        "18": "G45, I63-I69",
        "19": "I20-I25",
        "20": "I50, J81",
        "21": "E11-E14",
        "22": "DM + PROCED 1701",
    }

    table_rows = []
    for iid in ["18", "19", "20", "21", "22"]:
        r = rows[rows["indicador_id"] == iid]
        if r.empty:
            continue
        r_2024 = r[r["Ano"] == 2024]
        r_2025 = r[r["Ano"] == 2025]
        table_rows.append({
            "Indicador": indicator_label(iid, names.get(iid, "")),
            "CIE-10": cies.get(iid, ""),
            "N 2024": format_int(r_2024.iloc[0]["n_egresos"]) if not r_2024.empty else "",
            "Tasa 2024": format_indicator_value(r_2024.iloc[0]["tasa_x10000"], "por 10.000") if not r_2024.empty else "",
            "N 2025": format_int(r_2025.iloc[0]["n_egresos"]) if not r_2025.empty else "",
            "Tasa 2025": format_indicator_value(r_2025.iloc[0]["tasa_x10000"], "por 10.000") if not r_2025.empty else "",
        })

    display = pd.DataFrame(table_rows)
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.caption("**Tasa por 10.000 habitantes | Denominador:** Población FONASA 15+ años (PIV)")
    st.info(
        "Fuente: DEIS Egresos Hospitalarios (EH) 2024-2025. Los egresos se filtran por residentes de la "
        "Región Metropolitana, beneficiarios FONASA, de 15 años y más. El indicador 22 cruza el "
        "diagnóstico de diabetes (CIE-10 E10-E14) con código de procedimiento quirúrgico (prefijo 1701)."
    )

    st.download_button(
        "Descargar tasas de egresos (CSV)",
        data=csv_bytes(display),
        file_name=f"tasas_egresos_{level}_2024_2025.csv",
        mime="text/csv",
    )


def _render_metodologia_encabezado() -> None:
    st.markdown("""
    <div class="hero-panel">
        <div class="hero-title">Metodología</div>
        <div class="hero-copy">
            Documentación técnica del pipeline de cálculo de indicadores cardiovasculares
            para la Región Metropolitana. Fuentes: REM P4, FONASA (PIV) y DEIS (egresos hospitalarios).
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_metodologia_fuentes() -> None:
    st.markdown("""
    ### Fuentes de datos

    | Fuente | Descripción | Período |
    |--------|-------------|---------|
    | **REM Serie P** | Registro Estadístico Mensual - Programa de Salud Cardiovascular (PSCV), formulario P4 | 2024 - 2025 |
    | **FONASA PIV** | Población inscrita validada, 15 años y más, Región Metropolitana | 2023 - 2025 |
    | **DEIS Egresos** | Base de egresos hospitalarios del Departamento de Estadísticas e Información de Salud | 2024 - 2025 |
    """)

    st.caption(
        "REM = Registro Estadístico Mensual, PIV = Población Inscrita Validada, "
        "DEIS = Departamento de Estadísticas e Información de Salud, FONASA = Fondo Nacional de Salud."
    )


def _render_metodologia_indicadores() -> None:
    data = load_dashboard_data()
    egresos = load_egresos_data()
    sources = load_indicator_sources()

    st.markdown("### Indicadores calculados")

    rows = []
    indicator_ids = sorted(data["indicador_id"].unique(), key=indicator_sort_key)

    for iid in indicator_ids:
        rm_val_2024 = data[(data["nivel"] == "rm") & (data["Ano"] == 2024) & (data["indicador_id"] == iid)]
        rm_val_2025 = data[(data["nivel"] == "rm") & (data["Ano"] == 2025) & (data["indicador_id"] == iid)]

        nombre = ""
        if not rm_val_2024.empty:
            nombre = rm_val_2024.iloc[0]["nombre_indicador"]
        elif not rm_val_2025.empty:
            nombre = rm_val_2025.iloc[0]["nombre_indicador"]

        estado_2024 = rm_val_2024.iloc[0]["estado_calculo"] if not rm_val_2024.empty else ""
        estado_2025 = rm_val_2025.iloc[0]["estado_calculo"] if not rm_val_2025.empty else ""
        metodo = rm_val_2024.iloc[0]["metodo_calculo"] if not rm_val_2024.empty else (rm_val_2025.iloc[0]["metodo_calculo"] if not rm_val_2025.empty else "")

        estado_label = _estado_label(estado_2024, estado_2025)
        fuente = _fuente_indicador(iid)
        numerador_desc = SHORT_NUM.get(iid, "")
        denominador_desc = SHORT_DEN.get(iid, "")
        unidad = "por 10.000" if iid in ("18", "19", "20", "21", "22") else "%"

        rows.append({
            "ID": iid,
            "Nombre": nombre,
            "Fuente": fuente,
            "Numerador": numerador_desc,
            "Denominador": denominador_desc,
            "Unidad": unidad,
            "Estado": estado_label,
        })

    if not egresos.empty:
        for iid in ("18", "19", "20", "21", "22"):
            if iid not in indicator_ids:
                nombre = EGRESOS_NAMES.get(iid, "")
                rows.append({
                    "ID": iid,
                    "Nombre": nombre,
                    "Fuente": "DEIS Egresos",
                    "Numerador": SHORT_NUM.get(iid, ""),
                    "Denominador": SHORT_DEN.get(iid, ""),
                    "Unidad": "por 10.000",
                    "Estado": "Calculado",
                })

    display = pd.DataFrame(rows).sort_values("ID", key=lambda col: col.map(indicator_sort_key)).reset_index(drop=True)
    st.dataframe(display, use_container_width=True, hide_index=True)


def _fuente_indicador(iid: str) -> str:
    if iid in ("18", "19", "20", "21", "22"):
        return "DEIS Egresos + FONASA"
    if iid == "5":
        return "No disponible"
    return "REM P4 + FONASA PIV"


def _estado_label(est_2024: str, est_2025: str) -> str:
    partes = []
    for anio, est in [("2024", est_2024), ("2025", est_2025)]:
        if est == "calculado":
            partes.append(f"{anio}: Calculado")
        elif est == "proxy":
            partes.append(f"{anio}: Proxy")
        elif est:
            partes.append(f"{anio}: {est.capitalize()}")
    return ", ".join(partes) if partes else "No calculado"


def _render_metodologia_rem_codigos() -> None:
    sources = load_indicator_sources()
    if sources.empty:
        return

    st.markdown("### Trazabilidad REM P4 por código")
    st.caption("Detalle de cada código REM P4 utilizado en el cálculo de numeradores y denominadores.")

    source_display = sources.rename(
        columns={
            "indicador": "Indicador",
            "nombre_indicador": "Nombre",
            "rol": "Rol",
            "rem": "REM",
            "seccion": "Sección",
            "seccion_nombre": "Sección nombre",
            "codigo_prestacion": "Código",
            "detalle_prestacion": "Prestación",
            "nota_metodologica": "Nota",
        }
    )
    st.dataframe(
        source_display[
            [
                "Indicador", "Nombre", "Rol", "REM", "Sección",
                "Sección nombre", "Código", "Prestación", "Nota",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def _render_metodologia_validacion() -> None:
    validation = load_validation()

    st.markdown("### Validación RM 2024")
    st.caption(
        "Comparación entre los valores calculados por el pipeline y los valores oficiales de la planilla "
        "para la Región Metropolitana, año 2024."
    )

    if validation.empty:
        st.info("No hay archivo de validación disponible.")
        return

    st.dataframe(
        build_validation_display(validation),
        use_container_width=True,
        hide_index=True,
    )


def _render_metodologia_notas() -> None:
    st.markdown("### Notas metodológicas")
    st.markdown("""
    **Cobertura territorial:** Los indicadores 1 a 17 se calculan a nivel de establecimiento, comuna,
    servicio de salud y región. Los indicadores 18 a 22 tienen su propia página y se pueden desagregar
    por servicio de salud y comuna.

    **Población de referencia (PIV):** La población inscrita validada (PIV) de 15 años y más
    se obtiene de las bases de FONASA y se utiliza como denominador para los indicadores de
    cobertura (1, 3, 6, 8) y tasas de egresos (18 a 22).

    **Prevalencias estimadas:**
    - Hipertensión arterial (HTA): 27,6% de la población de 15 años y más, según Encuesta Nacional de Salud (ENS).
    - Diabetes mellitus tipo 2 (DM2): 12,3% de la población de 15 años y más, según ENS.

    **Indicadores 16 y 17 (ECV):** Para el año 2024 se utilizó un proxy debido a cambios en los códigos
    REM P4 entre 2024 y 2025.

    **Indicador 22 (amputación):** Se calcula cruzando el diagnóstico principal (DIAG1, códigos E10 a E14)
    con el código de procedimiento quirúrgico (PROCED_PPAL, prefijo 1701) en la base de egresos DEIS.

    **Indicador 15:** Solo disponible para 2025, ya que los códigos REM P4 requeridos no estaban
    disponibles en la Serie P 2024.

    **Tasas de egresos:** Se expresan por cada 10.000 habitantes. Denominador: Población FONASA 15+ años (PIV).
    """)

    st.markdown("### Fechas de extracción de datos")
    st.markdown("""
    | Fuente | Fecha de extracción |
    |--------|--------------------|
    | REM P4 y PIV FONASA - indicadores 2025 | 30 de enero de 2026 |
    | Datos para indicadores 2019, 2022-2024 | 20 de febrero de 2025 |
    | Tasas de hospitalización 2022-2024 | 13 de junio de 2025 |
    | Tasas de hospitalización 2025 | Preliminar, pendiente definitivo |
    | Corrección amputación pie DM y ECV 2022-2024 | 13 de junio de 2025 |
    """)


def render_methodology_page() -> None:
    _render_metodologia_encabezado()
    _render_metodologia_fuentes()
    _render_metodologia_indicadores()
    _render_metodologia_rem_codigos()
    _render_metodologia_notas()


def get_navigation_pages():
    return [
        st.Page(render_excel_like_page, title="Indicadores cardiovasculares RM", icon=":material/table_view:", default=True),
        st.Page(render_indicator_table_page, title="Indicadores REM P4", icon=":material/filter_alt:"),
        st.Page(render_egresos_page, title="Indicadores Egresos Hospitalarios", icon=":material/local_hospital:"),
        st.Page(render_methodology_page, title="Metodología", icon=":material/analytics:"),
    ]
