from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
BENEFICIARIOS_DIR = Path(
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\SEREMIRM - Estadistica\A Estadisticas Sanitarias y Demograficas\POBLACIONES\BENEFICIARIOS\Datos FONASA"
)
LOOKUP_PATH = BASE_DIR / "poblacion_inscrita_validada_15_mas_rm_establecimiento_2023_2025.csv"

OUTPUT_COMUNA = BASE_DIR / "beneficiarios_fonasa_15_mas_rm_comuna_2024_2025.csv"
OUTPUT_RESUMEN = BASE_DIR / "beneficiarios_fonasa_15_mas_rm_resumen_2024_2025.csv"

RM_REGION_NAME = "metropolitana de santiago"


def normalize_text(value: object) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("servicio de salud", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_lookup() -> pd.DataFrame:
    cols = ["IdComuna_master", "comuna_master", "IdServicio_master", "servicio_salud_master"]
    lookup = pd.read_csv(LOOKUP_PATH, dtype=str, usecols=cols)
    lookup = lookup.dropna(subset=["IdComuna_master", "comuna_master"])
    lookup = lookup.drop_duplicates(cols).copy()
    lookup["comuna_key"] = lookup["comuna_master"].map(normalize_text)
    lookup["servicio_key"] = lookup["servicio_salud_master"].map(normalize_text)
    return lookup


def parse_age_start(age_label: object) -> int | None:
    text = str(age_label or "").strip()
    match = re.match(r"^(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def aggregate_2024(lookup: pd.DataFrame) -> pd.DataFrame:
    path = BENEFICIARIOS_DIR / "T9625 Beneficiarios RM.xlsx"
    df = pd.read_excel(path, sheet_name="Respuesta", header=3, dtype=str)
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    df["Mes Información"] = pd.to_numeric(df["Mes Información"], errors="coerce")
    df["Edad"] = pd.to_numeric(df["Edad"], errors="coerce")
    df["Beneficiarios"] = pd.to_numeric(df["Beneficiarios"], errors="coerce").fillna(0)
    df = df[(df["Mes Información"] == 202412) & (df["Edad"] >= 15)].copy()

    df["comuna_key"] = df["Comuna"].map(normalize_text)
    df["servicio_key"] = df["Servicio de Salud"].map(normalize_text)

    grouped = (
        df.groupby(["comuna_key", "servicio_key"], as_index=False)["Beneficiarios"]
        .sum()
        .rename(columns={"Beneficiarios": "beneficiarios_fonasa_15_mas"})
    )
    out = grouped.merge(lookup, on=["comuna_key", "servicio_key"], how="left")
    out["Ano"] = 2024
    return out


def aggregate_2025(lookup: pd.DataFrame) -> pd.DataFrame:
    path = BENEFICIARIOS_DIR / "Beneficiarios 2025.csv"
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    df["edad_inicio"] = df["EDAD_TRAMO"].map(parse_age_start)
    df["BENEFICIARIOS"] = pd.to_numeric(df["BENEFICIARIOS"], errors="coerce").fillna(0)
    df["region_key"] = df["REGIÓN"].map(normalize_text)

    df = df[
        (df["MES_INFORMACION"] == "202512")
        & (df["region_key"] == RM_REGION_NAME)
        & (pd.to_numeric(df["edad_inicio"], errors="coerce") >= 15)
    ].copy()

    df["comuna_key"] = df["COMUNA"].map(normalize_text)
    grouped = (
        df.groupby("comuna_key", as_index=False)["BENEFICIARIOS"]
        .sum()
        .rename(columns={"BENEFICIARIOS": "beneficiarios_fonasa_15_mas"})
    )

    comuna_lookup = (
        lookup.sort_values(["IdComuna_master", "IdServicio_master"])
        .drop_duplicates("comuna_key")
        .copy()
    )
    out = grouped.merge(comuna_lookup, on="comuna_key", how="left")
    out["Ano"] = 2025
    return out


def finalize(detail: pd.DataFrame) -> pd.DataFrame:
    missing = detail[detail["IdComuna_master"].isna() | detail["IdServicio_master"].isna()]
    if not missing.empty:
        sample = missing[["Ano", "comuna_key", "servicio_key"]].fillna("").drop_duplicates()
        raise ValueError(
            "No se pudo homologar beneficiarios FONASA para algunas comunas/servicios: "
            + repr(sample.head(10).to_dict(orient="records"))
        )

    out = (
        detail[
            [
                "Ano",
                "IdServicio_master",
                "servicio_salud_master",
                "IdComuna_master",
                "comuna_master",
                "beneficiarios_fonasa_15_mas",
            ]
        ]
        .rename(
            columns={
                "IdServicio_master": "IdServicio",
                "servicio_salud_master": "servicio_salud",
                "IdComuna_master": "IdComuna",
                "comuna_master": "comuna",
            }
        )
        .copy()
    )
    out["beneficiarios_fonasa_15_mas"] = (
        pd.to_numeric(out["beneficiarios_fonasa_15_mas"], errors="coerce").fillna(0).round().astype("int64")
    )
    out = out.sort_values(["Ano", "IdServicio", "IdComuna"]).reset_index(drop=True)
    return out


def build_resumen(comuna_df: pd.DataFrame) -> pd.DataFrame:
    ss = (
        comuna_df.groupby(["Ano", "IdServicio", "servicio_salud"], as_index=False)["beneficiarios_fonasa_15_mas"]
        .sum()
        .sort_values(["Ano", "IdServicio"])
    )
    ss["nivel"] = "servicio_salud"
    rm = (
        comuna_df.groupby("Ano", as_index=False)["beneficiarios_fonasa_15_mas"]
        .sum()
        .assign(nivel="rm", IdServicio="", servicio_salud="")
    )
    resumen = pd.concat([ss, rm], ignore_index=True)
    return resumen[
        ["Ano", "nivel", "IdServicio", "servicio_salud", "beneficiarios_fonasa_15_mas"]
    ].sort_values(["Ano", "nivel", "IdServicio"])


def main() -> None:
    lookup = build_lookup()
    frames = [aggregate_2024(lookup), aggregate_2025(lookup)]
    comuna_df = finalize(pd.concat(frames, ignore_index=True))
    resumen_df = build_resumen(comuna_df)

    comuna_df.to_csv(OUTPUT_COMUNA, index=False, encoding="utf-8-sig")
    resumen_df.to_csv(OUTPUT_RESUMEN, index=False, encoding="utf-8-sig")

    print(f"Guardado comuna: {OUTPUT_COMUNA}")
    print(f"Guardado resumen: {OUTPUT_RESUMEN}")
    for year in sorted(comuna_df['Ano'].unique()):
        total = int(comuna_df.loc[comuna_df["Ano"] == year, "beneficiarios_fonasa_15_mas"].sum())
        print(f"{year}: RM beneficiarios FONASA 15+ = {total:,}")


if __name__ == "__main__":
    main()
