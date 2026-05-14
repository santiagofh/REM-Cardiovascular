from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
CONSOLIDADO_PATH = OUTPUT_DIR / "consolidado_indicadores_cardiovasculares.csv"
DETALLE_PATH = OUTPUT_DIR / "detalle_indicadores_establecimiento.csv"
DENOMINADOR_PATH = OUTPUT_DIR / "denominador_poblacion_inscrita.csv"
METADATA_PATH = OUTPUT_DIR / "metadata_cardiovascular.csv"
EGRESOS_PATH = OUTPUT_DIR / "indicadores_egresos_hospitalarios_detalle.csv"

EGRESOS_INDICADORES = {
    18: "Enfermedad cerebrovascular",
    19: "Enf. isquémicas del corazón",
    20: "Insuficiencia cardíaca",
    21: "Diabetes mellitus",
    22: "Amputación pie DM (proxy)",
}

PLANILLA_2024_RM = {
    18: {"tasa": 20.69, "n": 10572},
    19: {"tasa": 19.92, "n": 10177},
    20: {"tasa": 12.09, "n": 6178},
    21: {"tasa": None, "n": None},
    22: {"tasa": 7.70, "n": 3936},
}

SERVICIO_ORDEN = [
    "Servicio de Salud Metropolitano Norte",
    "Servicio de Salud Metropolitano Occidente",
    "Servicio de Salud Metropolitano Oriente",
    "Servicio de Salud Metropolitano Sur",
    "Servicio de Salud Metropolitano Sur Oriente",
    "SEREMI de Salud Metropolitana de Santiago",
]

ACCENT_REPLACEMENTS = str.maketrans({
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    "ñ": "n", "Ñ": "N",
})

INDICADORES_INFO = {
    "ind_01": {"nombre": "Cobertura HTA", "unit": "%", "orden": 1},
    "ind_02": {"nombre": "Control HTA", "unit": "%", "orden": 2},
    "ind_03": {"nombre": "Cobertura efectiva HTA", "unit": "%", "orden": 3},
    "ind_04": {"nombre": "HTA muy descompensadas", "unit": "%", "orden": 4},
    "ind_05": {"nombre": "Indice Madurez HEARTS", "unit": "%", "orden": 5},
    "ind_06": {"nombre": "Cobertura DM2", "unit": "%", "orden": 6},
    "ind_07": {"nombre": "Control DM2", "unit": "%", "orden": 7},
    "ind_08": {"nombre": "Cobertura efectiva DM2", "unit": "%", "orden": 8},
    "ind_09": {"nombre": "DM2 muy descompensadas", "unit": "%", "orden": 9},
    "ind_10": {"nombre": "DM2 compensada usuarias insulina", "unit": "%", "orden": 10},
    "ind_12b": {"nombre": "DM2 fondo de ojo vigente", "unit": "%", "orden": 12},
    "ind_13": {"nombre": "HTA evaluacion funcion renal", "unit": "%", "orden": 13},
    "ind_14": {"nombre": "DM2 evaluacion funcion renal", "unit": "%", "orden": 14},
    "ind_15": {"nombre": "DM+ERC tratamiento IECA/ARA II", "unit": "%", "orden": 15},
    "ind_16": {"nombre": "ECV antiagregante plaquetario", "unit": "%", "orden": 16},
    "ind_17": {"nombre": "ECV estatinas", "unit": "%", "orden": 17},
}


def slugify(text: str) -> str:
    return text.lower().translate(ACCENT_REPLACEMENTS).replace("/", "_").replace("-", "_").replace(" ", "_")


def format_int(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(round(value)):,}".replace(",", ".")


def format_pct(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:.2f}%"


def format_pp_delta(current: float, previous: float) -> str | None:
    if pd.isna(current) or pd.isna(previous):
        return None
    delta = current - previous
    return f"{delta:+.2f} pp"


def dataframe_to_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return buffer.getvalue()


@st.cache_data(show_spinner=False)
def load_consolidado() -> pd.DataFrame:
    if not CONSOLIDADO_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(CONSOLIDADO_PATH, low_memory=False)
    for col in df.columns:
        if col not in ["nivel_geografico", "indicador_id", "indicador_nombre"] + \
           [k for k in INDICADORES_INFO]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_detalle() -> pd.DataFrame:
    if not DETALLE_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(DETALLE_PATH, low_memory=False)
    for col in df.columns:
        if col not in ["IdEstablecimiento", "establecimiento_master", "IdServicio_master",
                       "servicio_salud_master", "IdComuna_master", "comuna_master",
                       "tipo_establecimiento_master", "dependencia_master"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_metadata() -> pd.DataFrame:
    if METADATA_PATH.exists():
        return pd.read_csv(METADATA_PATH)
    return pd.DataFrame(columns=["campo", "valor"])


def list_years() -> list[int]:
    df = load_consolidado()
    if df.empty or "Ano" not in df.columns:
        return [2024, 2025]
    years = sorted({int(y) for y in df["Ano"].dropna().unique()}, reverse=True)
    return years or [2024, 2025]


def safe_unique(series: pd.Series) -> list[str]:
    cleaned = series.fillna("").astype(str).str.strip().replace({"nan": "", "None": ""})
    return sorted({v for v in cleaned.tolist() if v})


def geo_columns(level: str) -> list[str]:
    if level == "establecimiento":
        return ["IdServicio_master", "servicio_salud_master", "IdComuna_master",
                "comuna_master", "IdEstablecimiento", "establecimiento_master",
                "tipo_establecimiento_master", "dependencia_master"]
    if level == "comuna":
        return ["IdServicio_master", "servicio_salud_master", "IdComuna_master", "comuna_master"]
    if level == "servicio_salud":
        return ["IdServicio_master", "servicio_salud_master"]
    if level == "rm":
        return []
    raise ValueError(f"Nivel no soportado: {level}")


def filter_by_geo(df: pd.DataFrame, level: str, filters: dict) -> pd.DataFrame:
    out = df.copy()
    if filters.get("servicio_salud") and "servicio_salud_master" in out.columns:
        out = out[out["servicio_salud_master"].astype(str) == str(filters["servicio_salud"])]
    if filters.get("comuna") and "comuna_master" in out.columns:
        out = out[out["comuna_master"].astype(str) == str(filters["comuna"])]
    if filters.get("establecimiento") and "establecimiento_master" in out.columns:
        out = out[out["establecimiento_master"].astype(str) == str(filters["establecimiento"])]
    return out


def render_geo_filters(df: pd.DataFrame, level: str, key_prefix: str) -> dict:
    filters: dict[str, str | None] = {
        "servicio_salud": None, "comuna": None, "establecimiento": None
    }
    scoped = df.copy()

    if "servicio_salud_master" in scoped.columns:
        opts = safe_unique(scoped["servicio_salud_master"])
        sel = st.selectbox("Servicio de Salud", ["(Todos)"] + opts, key=f"{key_prefix}_ss")
        if sel != "(Todos)":
            filters["servicio_salud"] = sel
            scoped = scoped[scoped["servicio_salud_master"].astype(str) == sel]

    if level in {"comuna", "establecimiento"} and "comuna_master" in scoped.columns:
        opts = safe_unique(scoped["comuna_master"])
        sel = st.selectbox("Comuna", ["(Todas)"] + opts, key=f"{key_prefix}_com")
        if sel != "(Todas)":
            filters["comuna"] = sel
            scoped = scoped[scoped["comuna_master"].astype(str) == sel]

    if level == "establecimiento" and "establecimiento_master" in scoped.columns:
        opts = safe_unique(scoped["establecimiento_master"])
        sel = st.selectbox("Establecimiento", ["(Todos)"] + opts, key=f"{key_prefix}_est")
        if sel != "(Todos)":
            filters["establecimiento"] = sel

    return filters


def build_indicator_row(
    detalle: pd.DataFrame, indicador_id: str, info: dict, year: int, filters: dict
) -> dict:
    num_col = f"{indicador_id}_num"
    den_col = f"{indicador_id}_den"
    pct_col = f"{indicador_id}_pct"

    df = detalle[detalle["Ano"] == year].copy() if "Ano" in detalle.columns else detalle.copy()
    df = filter_by_geo(df, "establecimiento", filters)

    numerador = df[num_col].sum() if num_col in df.columns else 0
    denominador = df[den_col].sum() if den_col in df.columns else 0
    cobertura = (numerador / denominador * 100) if denominador > 0 else None

    return {
        "id": indicador_id,
        "nombre": info["nombre"],
        "numerador": int(numerador),
        "denominador": int(denominador),
        "cobertura": cobertura,
        "unit": info["unit"],
    }


def render_home_page() -> None:
    st.title("Dashboard Cardiovascular 2024-2025")
    st.caption("Indicadores del Programa de Salud Cardiovascular (PSCV) - Region Metropolitana.")

    consolidado = load_consolidado()
    detalle = load_detalle()
    if detalle.empty:
        st.error("No se encontraron datos. Ejecute primero calcular_indicadores_cardiovasculares.py")
        st.stop()

    years = list_years()
    col_y, col_l = st.columns([1, 2])
    with col_y:
        year = st.selectbox("Ano", years, index=0, key="home_year")
    with col_l:
        level = st.selectbox("Nivel", ["rm", "servicio_salud", "comuna", "establecimiento"],
                             index=0, format_func=lambda x: x.replace("_", " ").title(), key="home_level")

    with st.sidebar:
        st.header("Filtros")
        filters = render_geo_filters(detalle, level, "home")

    rm_rows = []
    for ind_id, info in sorted(INDICADORES_INFO.items(), key=lambda x: x[1]["orden"]):
        row = build_indicator_row(detalle, ind_id, info, year, filters)
        rm_rows.append(row)

    cols = st.columns(3)
    for i, row in enumerate(rm_rows):
        with cols[i % 3]:
            pct = row["cobertura"]
            pct_str = format_pct(pct) if pct is not None else "N/D"
            st.metric(
                row["nombre"],
                pct_str,
                help=f"N: {format_int(row['numerador'])} | D: {format_int(row['denominador'])}"
            )

    st.markdown("### Tabla de indicadores")
    table_df = pd.DataFrame(rm_rows).rename(columns={
        "nombre": "Indicador", "numerador": "Numerador",
        "denominador": "Denominador", "cobertura": "Cobertura"
    })
    table_df["Cobertura"] = table_df["Cobertura"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/D"
    )
    st.dataframe(table_df[["Indicador", "Numerador", "Denominador", "Cobertura"]],
                 use_container_width=True, height=540,
                 column_config={
                     "Numerador": st.column_config.NumberColumn(format="%d"),
                     "Denominador": st.column_config.NumberColumn(format="%d"),
                 })

    st.markdown("### Evolucion anual")
    trend_data = []
    for ind_id, info in INDICADORES_INFO.items():
        pct_col = f"{ind_id}_pct"
        if pct_col not in detalle.columns:
            continue
        for y in years:
            sub = detalle[detalle["Ano"] == y] if "Ano" in detalle.columns else detalle
            val = sub[pct_col].sum() / len(sub) if len(sub) > 0 else None
            if pd.notna(val):
                trend_data.append({"Ano": str(y), "Indicador": info["nombre"], "Valor": val})

    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        fig = px.line(trend_df, x="Ano", y="Valor", color="Indicador",
                      markers=True, title="Evolucion por indicador")
        fig.update_layout(height=400, legend_title=None,
                          plot_bgcolor="white", paper_bgcolor="white")
        fig.update_yaxes(ticksuffix="%", showgrid=True, gridcolor="#D9E6F2")
        st.plotly_chart(fig, use_container_width=True)

    excel_sheets = {"Indicadores": table_df}
    if not consolidado.empty:
        excel_sheets["Consolidado"] = consolidado
    excel_bytes = dataframe_to_excel_bytes(excel_sheets)
    st.download_button("Descargar en Excel", data=excel_bytes,
                       file_name=f"cardiovascular_{year}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def render_detail_page() -> None:
    st.title("Detalle por establecimiento")
    st.caption("Exploracion de indicadores a nivel de establecimiento.")

    detalle = load_detalle()
    if detalle.empty:
        st.error("No hay datos disponibles.")
        st.stop()

    years = list_years()
    year = st.selectbox("Ano", years, index=0, key="det_year")

    ind_options = {v["nombre"]: k for k, v in INDICADORES_INFO.items()}
    sel_ind_name = st.selectbox("Indicador", list(ind_options.keys()), index=0, key="det_ind")
    ind_id = ind_options[sel_ind_name]

    num_col = f"{ind_id}_num"
    den_col = f"{ind_id}_den"
    pct_col = f"{ind_id}_pct"

    df = detalle[detalle["Ano"] == year].copy() if "Ano" in detalle.columns else detalle.copy()
    df = df[df["es_aps"] == True].copy() if "es_aps" in df.columns else df

    df = df.dropna(subset=[pct_col])
    df = df.sort_values(pct_col, ascending=False)

    top_n = st.slider("Mostrar cuantos establecimientos", 5, 50, 20, key="det_top")

    chart_df = df.head(top_n).copy()
    fig = px.bar(chart_df, x=pct_col, y="establecimiento_master",
                 orientation="h", text=pct_col,
                 color=pct_col, color_continuous_scale=["#A7D3F3", "#2E75B6", "#1F4E79"],
                 hover_data={num_col: ":,.0f", den_col: ":,.0f"})
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(height=max(400, 25 * top_n), margin=dict(l=20, r=35, t=20, b=20),
                      coloraxis_showscale=False, xaxis_title="%",
                      yaxis_title="", plot_bgcolor="white", paper_bgcolor="white")
    fig.update_xaxes(showgrid=True, gridcolor="#D9E6F2")
    st.plotly_chart(fig, use_container_width=True)

    display = df[["IdEstablecimiento", "establecimiento_master", "servicio_salud_master",
                  "comuna_master", num_col, den_col, pct_col]].rename(columns={
        "IdEstablecimiento": "Codigo", "establecimiento_master": "Establecimiento",
        "servicio_salud_master": "Servicio", "comuna_master": "Comuna",
        num_col: "Numerador", den_col: "Denominador", pct_col: "Cobertura"
    })
    display["Cobertura"] = display["Cobertura"].apply(
        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/D"
    )
    st.dataframe(display, use_container_width=True, height=480)


def render_method_page() -> None:
    st.title("Control y metodologia")
    st.caption("Trazabilidad metodologica de los indicadores cardiovasculares.")

    st.markdown("""
    ### Fuentes de datos
    - **Serie P (REM P4)**: Programa de Salud Cardiovascular - datos mensuales por establecimiento
    - **FONASA T8009**: Poblacion inscrita validada APS Region Metropolitana
    - **Maestro DEIS**: Establecimientos con codigos, dependencia y nivel de atencion

    ### Indicadores calculados

    | # | Indicador | Numerador | Denominador |
    |---|-----------|-----------|-------------|
    | 1 | Cobertura HTA | P4150601 (Col01) | PIV 15+ x 27.6% |
    | 2 | Control HTA | P4180200 + P4200100 | P4150601 (Col01) |
    | 3 | Cobertura efectiva HTA | P4180200 + P4200100 | PIV 15+ x 27.6% |
    | 4 | HTA muy descompensadas | P4200400 (Col01) | P4150601 (Col01) |
    | 5 | Indice Madurez HEARTS | P4190808 (Col01) | P4150601 (Col01) |
    | 6 | Cobertura DM2 | P4150602 (Col01) | PIV 15+ x 12.3% |
    | 7 | Control DM2 | P4180300 + P4200200 | P4150602 (Col01) |
    | 8 | Cobertura efectiva DM2 | P4180300 + P4200200 | PIV 15+ x 12.3% |
    | 9 | DM2 muy descompensadas | P4190960 (Col01) | P4150602 (Col01) |
    | 10 | DM2 compensada usuarias insulina | P4200700 | P4180800 |
    | 12b | DM2 fondo de ojo vigente | P4190950 (Col01) | P4150602 (Col01) |
    | 13 | HTA evaluacion funcion renal | P4301080 (Col01) | P4150601 (Col01) |
    | 14 | DM2 evaluacion funcion renal | P4301040 (Col01) | P4150602 (Col01) |
    | 15 | DM+ERC tratamiento IECA/ARA II | P4200800 | P4200600 |
    | 16 | ECV antiagregante plaquetario | P4190930 (Col01) | P4190900 + P4190910 |
    | 17 | ECV estatinas | P4190940 (Col01) | P4190900 + P4190910 |

    ### Supuestos metodologicos
    - Los numeradores anuales se obtienen sumando registros mensuales REM P4
    - Solo se incluyen establecimientos APS (NivelAtencionEstabglosa contiene "Primario")
    - Prevalencias ENS 2016-2017: HTA 27.6%, DM2 12.3%
    - Denominador poblacional: FONASA T8009, poblacion inscrita validada 15+ en APS RM
    - Filtro region: RM (codigo 13)
    """)

    st.markdown("### Documentos de referencia")
    st.link_button("Manual REM Serie P 2025",
                   "https://repositoriodeis.minsal.cl/ContenidoSitioWeb2020/REM/2025/SERIE/MANUAL_REM_P_2025_Version_1.2.pdf",
                   use_container_width=False)
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("Diccionario REM A05 2025",
                       "https://repositoriodeis.minsal.cl/ContenidoSitioWeb2020/REM/2025/Diccionarios/DICCIONARIO%20CODIGOS%20SA_25_V1.5.xlsm",
                       use_container_width=False)
    with col2:
        st.link_button("Diccionario REM P4 2025",
                       "https://repositoriodeis.minsal.cl/ContenidoSitioWeb2020/REM/2025/Diccionarios/DICCIONARIO%20CODIGOS%20SP_25_V1.0.xlsm",
                       use_container_width=False)

    detalle = load_detalle()
    st.markdown("### Resumen de datos cargados")
    if not detalle.empty:
        info = [
            ("Establecimientos", format_int(detalle["IdEstablecimiento"].nunique())),
            ("Anos disponibles", ", ".join(str(int(y)) for y in sorted(detalle["Ano"].dropna().unique())) if "Ano" in detalle.columns else "N/A"),
            ("Registros totales", format_int(len(detalle))),
            ("Establecimientos APS", format_int(detalle["es_aps"].sum()) if "es_aps" in detalle.columns else "N/A"),
        ]
        for label, value in info:
            st.markdown(f"- **{label}:** {value}")


@st.cache_data(show_spinner=False)
def load_egresos() -> pd.DataFrame:
    if not EGRESOS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(EGRESOS_PATH, low_memory=False)


def render_egresos_page() -> None:
    st.title("Egresos Hospitalarios Cardiovasculares")
    st.caption("Tasas de egresos hospitalarios x 10,000 hab. FONASA 15+ años. RM 2020-2024.")

    df = load_egresos()
    if df.empty:
        st.error("Ejecute primero calcular_indicadores_egresos.py")
        st.stop()

    years = sorted(df["Ano"].unique(), reverse=True)
    ind_ids = sorted(EGRESOS_INDICADORES.keys())
    niveles = ["RM", "Servicio de Salud", "Comuna"]

    with st.sidebar:
        st.header("Filtros egresos")
        sel_year = st.selectbox("Año", years, index=0, key="egr_year")
        sel_nivel = st.radio("Nivel geográfico", niveles, index=0, key="egr_nivel")
        sel_ind = st.selectbox(
            "Indicador",
            ind_ids,
            index=0,
            format_func=lambda x: f"{x}. {EGRESOS_INDICADORES[x]}",
            key="egr_ind",
        )

        base_rm = df[(df["comuna_nombre"] == "RM Total") & (df["Ano"] == sel_year) & (df["indicador_id"] == sel_ind)]
        tasa_rm = base_rm["tasa_x10000"].iloc[0] if not base_rm.empty else None

        sel_servicio = None
        sel_comuna = None
        if sel_nivel == "Servicio de Salud":
            servicios = sorted(df[df["servicio_salud"].isin(SERVICIO_ORDEN)]["servicio_salud"].unique())
            sel_servicio = st.selectbox("Servicio de Salud", servicios, key="egr_ss")
        elif sel_nivel == "Comuna":
            servicios = sorted(df[df["servicio_salud"].isin(SERVICIO_ORDEN)]["servicio_salud"].unique())
            sel_servicio = st.selectbox("Servicio de Salud", ["(Todos)"] + servicios, key="egr_ss2")
            comunas_df = df[(df["comuna_nombre"] != "RM Total") & (df["Ano"] == sel_year) & (df["indicador_id"] == sel_ind)]
            if sel_servicio and sel_servicio != "(Todos)":
                comunas_df = comunas_df[comunas_df["servicio_salud"] == sel_servicio]
            comunas = sorted(comunas_df["comuna_nombre"].unique())
            sel_comuna = st.selectbox("Comuna", comunas, key="egr_com")

    f_rm = df[(df["comuna_nombre"] == "RM Total") & (df["Ano"] == sel_year)]
    if tasa_rm:
        st.subheader(f"RM: {tasa_rm:.2f} x 10,000     |     {EGRESOS_INDICADORES[sel_ind]} {sel_year}")

    col1, col2, col3, col4, col5 = st.columns(5)
    for i, ind_id in enumerate(ind_ids):
        r = f_rm[f_rm["indicador_id"] == ind_id]
        if r.empty:
            continue
        t = r["tasa_x10000"].iloc[0]
        plan = PLANILLA_2024_RM.get(ind_id, {})
        with [col1, col2, col3, col4, col5][i]:
            delta = None
            if plan["tasa"] and sel_year == 2024:
                delta = f"{t - plan['tasa']:+.2f} vs planilla"
            n_val = int(r["n_egresos"].iloc[0])
            st.metric(
                f"IND{ind_id}",
                f"{t:.2f}",
                delta=delta,
                help=f"N: {n_val:,} | Denominador: 5.108.594",
            )

    st.markdown("---")

    # --- MAIN CHART ---
    if sel_nivel == "RM":
        chart_data = df[(df["comuna_nombre"] == "RM Total") & (df["indicador_id"] == sel_ind)].copy()
        chart_label = "RM"
    elif sel_nivel == "Servicio de Salud":
        chart_data = df[(df["servicio_salud"].isin(SERVICIO_ORDEN)) & (df["Ano"] == sel_year) & (df["indicador_id"] == sel_ind)].copy()
        chart_data = chart_data.groupby("servicio_salud", as_index=False).agg({"n_egresos": "sum", "tasa_x10000": "sum"})
        chart_label = "Servicio de Salud"
        chart_data = chart_data[chart_data["servicio_salud"].isin(SERVICIO_ORDEN)]
        chart_data["servicio_salud"] = pd.Categorical(chart_data["servicio_salud"], categories=SERVICIO_ORDEN, ordered=True)
        chart_data = chart_data.sort_values("servicio_salud")
    else:
        base = df[(df["comuna_nombre"] != "RM Total") & (df["Ano"] == sel_year) & (df["indicador_id"] == sel_ind)].copy()
        if sel_comuna:
            base = base[base["comuna_nombre"] == sel_comuna]
        elif sel_servicio and sel_servicio != "(Todos)":
            base = base[base["servicio_salud"] == sel_servicio]
        chart_data = base.sort_values("tasa_x10000", ascending=False)
        chart_label = "Comuna"

    with st.container(border=True):
        if not chart_data.empty:
            if sel_nivel == "RM":
                fig = px.bar(
                    chart_data, x="Ano", y="tasa_x10000",
                    color="Ano", text="tasa_x10000",
                    title=f"{EGRESOS_INDICADORES[sel_ind]} - Evolución RM",
                    labels={"tasa_x10000": "Tasa x 10,000", "Ano": "Año"},
                    color_continuous_scale="Blues",
                )
                fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            else:
                fig = px.bar(
                    chart_data,
                    x="tasa_x10000", y=chart_label,
                    orientation="h",
                    color="tasa_x10000",
                    text="tasa_x10000",
                    title=f"{EGRESOS_INDICADORES[sel_ind]} por {chart_label} - {sel_year}",
                    labels={"tasa_x10000": "Tasa x 10,000"},
                    color_continuous_scale="Blues",
                )
                fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_layout(height=420, plot_bgcolor="white", paper_bgcolor="white",
                              xaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # --- TREND CHART ---
    with st.container(border=True):
        trend = df[(df["comuna_nombre"] == "RM Total") & (df["indicador_id"] == sel_ind)].copy()
        if len(trend) > 1:
            fig2 = px.line(
                trend, x="Ano", y="tasa_x10000",
                markers=True, text="tasa_x10000",
                title=f"Tendencia {EGRESOS_INDICADORES[sel_ind]} - RM 2020-2024",
                labels={"tasa_x10000": "Tasa x 10,000", "Ano": "Año"},
            )
            fig2.update_traces(texttemplate="%{text:.2f}", textposition="top center",
                               line=dict(color="#1F4E79", width=3), marker=dict(size=10, color="#006FB3"))
            fig2.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white",
                               xaxis=dict(dtick=1, showgrid=True, gridcolor="#E5E5E5"),
                               yaxis=dict(showgrid=True, gridcolor="#E5E5E5"))
            # Add planilla reference line for 2024
            plan_val = PLANILLA_2024_RM.get(sel_ind, {}).get("tasa")
            if plan_val and 2024 in trend["Ano"].values:
                fig2.add_hline(y=plan_val, line_dash="dash", line_color="red",
                               annotation_text=f"Planilla 2024: {plan_val:.2f}",
                               annotation_position="bottom right")
            st.plotly_chart(fig2, use_container_width=True)

    # --- COMPARISON TABLE ---
    with st.container(border=True):
        st.markdown("**Todos los indicadores - Comparativo RM 2024**")
        comp = df[(df["comuna_nombre"] == "RM Total") & (df["Ano"] == 2024)].copy()
        rows = []
        for ind_id in ind_ids:
            r = comp[comp["indicador_id"] == ind_id]
            if r.empty:
                continue
            t = r["tasa_x10000"].iloc[0]
            n = int(r["n_egresos"].iloc[0])
            plan = PLANILLA_2024_RM.get(ind_id, {})
            tp = plan.get("tasa")
            np_ = plan.get("n")
            diff = (t - tp) if tp else None
            diff_pct = ((t - tp) / tp * 100) if tp else None
            rows.append({
                "IND": ind_id,
                "Indicador": EGRESOS_INDICADORES[ind_id],
                "N calc": n,
                "N planilla": str(np_) if np_ else "N/A",
                "Tasa calc": f"{t:.2f}",
                "Tasa planilla": f"{tp:.2f}" if tp else "N/A",
                "Diferencia": f"{diff:+.2f} ({diff_pct:+.1f}%)" if diff_pct is not None else "N/A",
            })
        comp_df = pd.DataFrame(rows)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # --- INFO FOOTER ---
    st.caption("Denominador: 5.108.594 (Población FONASA 15+ RM) | Datos: DEIS Egresos Hospitalarios | Planilla referencia: Planilla indicadores macrozonales 2026")


def get_navigation_pages():
    return [
        st.Page(render_home_page, title="Inicio", icon=":material/home:", default=True),
        st.Page(render_detail_page, title="Detalle establecimiento", icon=":material/location_city:", url_path="detalle"),
        st.Page(render_egresos_page, title="Egresos hospitalarios", icon=":material/local_hospital:", url_path="egresos"),
        st.Page(render_method_page, title="Control y metodologia", icon=":material/fact_check:", url_path="metodologia"),
    ]
