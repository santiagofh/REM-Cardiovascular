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

FONASA_SOURCES = {
    2023: {
        "ano_inscritos": 2022,
        "base_pago": 2023,
        "path": Path(
            r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2022 (Base pago 2023)\T5385_Poblacion_Inscrita_RM.xlsx"
        ),
        "sheets": ["Municipales", "Otras", "Servicio Salud"],
        "header_row": 5,
        "layout": "2022_rm",
    },
    2024: {
        "ano_inscritos": 2023,
        "base_pago": 2024,
        "path": Path(
            r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2023 (Base pago 2024)\Copia de T6603_Inscritos.xlsx"
        ),
        "sheets": ["Respuesta M", "Respuesta S"],
        "header_row": 5,
        "layout": "2023_nacional",
    },
    2025: {
        "ano_inscritos": 2024,
        "base_pago": 2025,
        "path": Path(
            r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\FONASA\Poblacion fonasa inscrita x comuna\INSCRITOS\Datos FONASA\Inscritos 2024 (Base pago 2025)\T8009_Inscritos_RM.xlsx"
        ),
        "sheets": ["Respuesta"],
        "header_row": 4,
        "layout": "2024_rm",
    },
}

DENOMINATOR_CODE_ALIASES = {
    "311001": "201674",
}

PREVALENCIA_HTA = 0.276
PREVALENCIA_DM2 = 0.123
CSV_ENCODING = "utf-8-sig"


def code_text(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )


def to_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype("int64")


def build_master_lookup() -> pd.DataFrame:
    cols = [
        "EstablecimientoCodigoAntiguo",
        "EstablecimientoCodigo",
        "EstablecimientoCodigoMadreNuevo",
        "RegionCodigo",
        "RegionGlosa",
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
    for col in [
        "EstablecimientoCodigoAntiguo",
        "EstablecimientoCodigo",
        "EstablecimientoCodigoMadreNuevo",
        "RegionCodigo",
        "SeremiSaludCodigo_ServicioDeSaludCodigo",
        "ComunaCodigo",
    ]:
        master[col] = code_text(master[col])

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


def read_sheet(path: Path, sheet_name: str, header_row: int) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, header=header_row - 1)


def standardize_frame(df: pd.DataFrame, ano_indicador: int, layout: str, sheet_name: str) -> pd.DataFrame:
    if layout == "2022_rm":
        out = df.rename(
            columns={
                "Código Región": "RegionCodigo",
                "Nombre Región": "RegionGlosa",
                "Código Serv. Salud": "IdServicio_den",
                "Nombre Serv. Salud": "servicio_salud_denominador",
                "Código Comuna": "IdComuna_den",
                "Nombre Comuna": "comuna_denominador",
                "Código Establecimiento": "IdEstablecimiento",
                "Nombre Establecimiento": "establecimiento_denominador",
                "Sexo": "sexo",
                "Edad": "edad",
                "Inscritos": "inscritos",
            }
        )
        dependencia = {
            "Municipales": "Municipal",
            "Otras": "ONG",
            "Servicio Salud": "Servicio de Salud",
        }
        out["dependencia_denominador"] = dependencia.get(sheet_name, "")
    elif layout == "2023_nacional":
        out = df.rename(
            columns={
                "Servicio de Salud": "servicio_salud_denominador",
                "Código Comuna": "IdComuna_den",
                "Comuna": "comuna_denominador",
                "Dependencia Adm.": "dependencia_denominador",
                "Código Centro": "IdEstablecimiento",
                "Centro": "establecimiento_denominador",
                "Sexo": "sexo",
                "Edad": "edad",
                "Inscritos": "inscritos",
            }
        )
        out["RegionCodigo"] = ""
        out["RegionGlosa"] = ""
        out["IdServicio_den"] = ""
    elif layout == "2024_rm":
        out = df.rename(
            columns={
                "Servicio de Salud": "servicio_salud_denominador",
                "Dependencia": "dependencia_denominador",
                "Comuna": "comuna_denominador",
                "Código Centro": "IdEstablecimiento",
                "Nombre Centro": "establecimiento_denominador",
                "Sexo": "sexo",
                "Edad": "edad",
                "Inscritos": "inscritos",
            }
        )
        out["RegionCodigo"] = "13"
        out["RegionGlosa"] = "Región Metropolitana de Santiago"
        out["IdServicio_den"] = ""
        out["IdComuna_den"] = ""
    else:
        raise ValueError(f"Layout no soportado: {layout}")

    required = [
        "RegionCodigo",
        "RegionGlosa",
        "IdServicio_den",
        "servicio_salud_denominador",
        "dependencia_denominador",
        "IdComuna_den",
        "comuna_denominador",
        "IdEstablecimiento",
        "establecimiento_denominador",
        "sexo",
        "edad",
        "inscritos",
    ]
    for col in required:
        if col not in out.columns:
            out[col] = ""

    out = out[required].copy()
    out["AnoIndicador"] = ano_indicador
    out["IdEstablecimiento_denominador_original"] = code_text(out["IdEstablecimiento"])
    out["IdEstablecimiento"] = out["IdEstablecimiento_denominador_original"].replace(
        DENOMINATOR_CODE_ALIASES
    )
    out["IdComuna_den"] = code_text(out["IdComuna_den"])
    out["IdServicio_den"] = code_text(out["IdServicio_den"])
    out["edad"] = pd.to_numeric(out["edad"], errors="coerce")
    out["inscritos"] = to_int(out["inscritos"])
    out["sexo"] = out["sexo"].astype(str).str.strip()
    out["servicio_salud_denominador"] = out["servicio_salud_denominador"].astype(str).str.strip()
    out["dependencia_denominador"] = out["dependencia_denominador"].astype(str).str.strip()
    out["comuna_denominador"] = out["comuna_denominador"].astype(str).str.strip()
    out["establecimiento_denominador"] = out["establecimiento_denominador"].astype(str).str.strip()
    return out


def load_population_detail() -> pd.DataFrame:
    frames = []
    for ano_indicador, cfg in FONASA_SOURCES.items():
        for sheet_name in cfg["sheets"]:
            raw = read_sheet(cfg["path"], sheet_name, cfg["header_row"])
            standard = standardize_frame(raw, ano_indicador, cfg["layout"], sheet_name)

            if cfg["layout"] == "2023_nacional":
                standard = standard[
                    standard["IdComuna_den"].astype(str).str.startswith("13", na=False)
                ].copy()
                standard["RegionCodigo"] = "13"
                standard["RegionGlosa"] = "Región Metropolitana de Santiago"

            if cfg["layout"] == "2022_rm":
                standard = standard[standard["RegionCodigo"].astype(str).eq("13")].copy()

            standard["AnoInscritos"] = cfg["ano_inscritos"]
            standard["BasePago"] = cfg["base_pago"]
            frames.append(standard)

    detail = pd.concat(frames, ignore_index=True)
    detail = detail[detail["edad"].ge(15)].copy()
    return detail


def aggregate_population(detail: pd.DataFrame, master: pd.DataFrame) -> pd.DataFrame:
    base_cols = [
        "AnoIndicador",
        "AnoInscritos",
        "BasePago",
        "IdEstablecimiento",
        "IdEstablecimiento_denominador_original",
        "servicio_salud_denominador",
        "dependencia_denominador",
        "comuna_denominador",
        "establecimiento_denominador",
    ]

    total = (
        detail.groupby(base_cols, dropna=False, as_index=False)["inscritos"]
        .sum()
        .rename(columns={"inscritos": "poblacion_inscrita_validada_15_mas"})
    )

    hombres = (
        detail[detail["sexo"].eq("Hombres")]
        .groupby(base_cols, dropna=False, as_index=False)["inscritos"]
        .sum()
        .rename(columns={"inscritos": "poblacion_inscrita_validada_15_mas_hombres"})
    )
    mujeres = (
        detail[detail["sexo"].eq("Mujeres")]
        .groupby(base_cols, dropna=False, as_index=False)["inscritos"]
        .sum()
        .rename(columns={"inscritos": "poblacion_inscrita_validada_15_mas_mujeres"})
    )

    out = total.merge(hombres, on=base_cols, how="left").merge(mujeres, on=base_cols, how="left")
    out["poblacion_inscrita_validada_15_mas_hombres"] = (
        pd.to_numeric(out["poblacion_inscrita_validada_15_mas_hombres"], errors="coerce")
        .fillna(0)
        .astype("int64")
    )
    out["poblacion_inscrita_validada_15_mas_mujeres"] = (
        pd.to_numeric(out["poblacion_inscrita_validada_15_mas_mujeres"], errors="coerce")
        .fillna(0)
        .astype("int64")
    )

    out["poblacion_estimada_hta_15_mas"] = (
        out["poblacion_inscrita_validada_15_mas"] * PREVALENCIA_HTA
    ).round(3)
    out["poblacion_estimada_dm2_15_mas"] = (
        out["poblacion_inscrita_validada_15_mas"] * PREVALENCIA_DM2
    ).round(3)

    out = out.merge(
        master,
        left_on="IdEstablecimiento",
        right_on="IdEstablecimiento_lookup",
        how="left",
    ).drop(columns=["IdEstablecimiento_lookup"])

    out = out.rename(
        columns={
            "EstablecimientoCodigo": "EstablecimientoCodigo_master",
            "EstablecimientoCodigoAntiguo": "EstablecimientoCodigoAntiguo_master",
            "EstablecimientoCodigoMadreNuevo": "codigo_madre_master",
            "RegionCodigo": "RegionCodigo_master",
            "RegionGlosa": "RegionGlosa_master",
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
    )
    out["sin_match_master"] = out["establecimiento_master"].isna()
    return out


def build_summary(agg: pd.DataFrame) -> pd.DataFrame:
    summary = (
        agg.groupby("AnoIndicador", as_index=False)
        .agg(
            ano_inscritos=("AnoInscritos", "first"),
            base_pago=("BasePago", "first"),
            establecimientos_con_denom=("IdEstablecimiento", "nunique"),
            establecimientos_con_match_master=("sin_match_master", lambda s: int((~s).sum())),
            establecimientos_aps=("es_aps", lambda s: int(pd.Series(s).fillna(False).sum())),
            poblacion_inscrita_validada_15_mas_rm=("poblacion_inscrita_validada_15_mas", "sum"),
            poblacion_inscrita_validada_15_mas_hombres_rm=(
                "poblacion_inscrita_validada_15_mas_hombres",
                "sum",
            ),
            poblacion_inscrita_validada_15_mas_mujeres_rm=(
                "poblacion_inscrita_validada_15_mas_mujeres",
                "sum",
            ),
            poblacion_estimada_hta_15_mas_rm=("poblacion_estimada_hta_15_mas", "sum"),
            poblacion_estimada_dm2_15_mas_rm=("poblacion_estimada_dm2_15_mas", "sum"),
        )
        .sort_values("AnoIndicador")
    )
    summary["poblacion_estimada_hta_15_mas_rm"] = summary[
        "poblacion_estimada_hta_15_mas_rm"
    ].round(3)
    summary["poblacion_estimada_dm2_15_mas_rm"] = summary[
        "poblacion_estimada_dm2_15_mas_rm"
    ].round(3)
    return summary


def write_dictionary(paths: dict[str, Path]) -> None:
    dictionary = {
        "metadata": {
            "generado_en": pd.Timestamp.now().isoformat(),
            "maestro_establecimientos": str(MASTER_PATH),
            "proyecto": "REM-Cardiovascular",
            "alcance": "Población inscrita y validada de 15 años y más para estimación de coberturas cardiovasculares",
        },
        "fuentes": {
            str(ano): {
                "ano_indicador": ano,
                "ano_inscritos": cfg["ano_inscritos"],
                "base_pago": cfg["base_pago"],
                "path": str(cfg["path"]),
                "sheets": cfg["sheets"],
            }
            for ano, cfg in FONASA_SOURCES.items()
        },
        "supuestos": [
            "Se usa población FONASA inscrita y validada de 15 años y más como base de cobertura.",
            "La prevalencia estimada para HTA es 27.6%.",
            "La prevalencia estimada para DM2 es 12.3%.",
            "El alias 311001 -> 201674 se aplica para homologar FONASA con el maestro DEIS/REM.",
            "La base 2022 (base pago 2023) se usa como denominador del año indicador 2023.",
            "La base 2023 (base pago 2024) se usa como denominador del año indicador 2024.",
            "La base 2024 (base pago 2025) se usa como denominador del año indicador 2025.",
        ],
        "columnas_csv_principal": {
            "AnoIndicador": "Año del indicador al que se aplicará el denominador.",
            "AnoInscritos": "Año de corte de inscritos FONASA.",
            "BasePago": "Año de base de pago informado por FONASA.",
            "IdEstablecimiento": "Código homologado del establecimiento.",
            "IdEstablecimiento_denominador_original": "Código original observado en la base FONASA.",
            "servicio_salud_denominador": "Servicio de salud según base FONASA.",
            "dependencia_denominador": "Dependencia según base FONASA.",
            "comuna_denominador": "Comuna según base FONASA.",
            "establecimiento_denominador": "Nombre del centro según base FONASA.",
            "poblacion_inscrita_validada_15_mas": "Población inscrita y validada de 15 años y más.",
            "poblacion_inscrita_validada_15_mas_hombres": "Población inscrita y validada de 15 años y más, hombres.",
            "poblacion_inscrita_validada_15_mas_mujeres": "Población inscrita y validada de 15 años y más, mujeres.",
            "poblacion_estimada_hta_15_mas": "Población estimada con HTA = población 15+ x 0.276.",
            "poblacion_estimada_dm2_15_mas": "Población estimada con DM2 = población 15+ x 0.123.",
            "codigo_madre_master": "Código madre del establecimiento según maestro.",
            "IdServicio_master": "Código de servicio de salud según maestro.",
            "servicio_salud_master": "Servicio de salud según maestro.",
            "tipo_establecimiento_master": "Tipo de establecimiento según maestro.",
            "establecimiento_master": "Nombre del establecimiento según maestro.",
            "dependencia_master": "Dependencia administrativa según maestro.",
            "nivel_atencion_master": "Nivel de atención según maestro.",
            "IdComuna_master": "Código de comuna según maestro.",
            "comuna_master": "Comuna según maestro.",
            "estado_funcionamiento_master": "Estado de funcionamiento según maestro.",
            "es_aps": "True si el maestro clasifica el establecimiento como nivel primario.",
            "sin_match_master": "True si el establecimiento no logró homologarse con el maestro.",
        },
        "archivos_generados": {name: str(path) for name, path in paths.items()},
    }
    paths["dictionary"].write_text(
        json.dumps(dictionary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "csv_main": OUTPUT_DIR / "poblacion_inscrita_validada_15_mas_rm_establecimiento_2023_2025.csv",
        "csv_summary": OUTPUT_DIR / "poblacion_inscrita_validada_15_mas_rm_resumen_anual_2023_2025.csv",
        "dictionary": OUTPUT_DIR / "diccionario_poblacion_inscrita_validada_15_mas_rm_2023_2025.json",
    }

    master = build_master_lookup()
    detail = load_population_detail()
    agg = aggregate_population(detail, master)
    summary = build_summary(agg)

    agg.to_csv(paths["csv_main"], index=False, encoding=CSV_ENCODING)
    summary.to_csv(paths["csv_summary"], index=False, encoding=CSV_ENCODING)
    write_dictionary(paths)

    print(
        json.dumps(
            {
                "csv_principal": str(paths["csv_main"]),
                "csv_resumen": str(paths["csv_summary"]),
                "diccionario": str(paths["dictionary"]),
                "filas_establecimiento": int(len(agg)),
                "anios_denominador": sorted(agg["AnoIndicador"].unique().tolist()),
                "poblacion_rm_2025": int(
                    summary.loc[
                        summary["AnoIndicador"].eq(2025),
                        "poblacion_inscrita_validada_15_mas_rm",
                    ].iloc[0]
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
