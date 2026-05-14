from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
WORKBOOK_PATH = PROJECT_DIR / "Planilla indicadores y fechas reuniones macrozonales 2026.xlsx"
PANEL_PATH = BASE_DIR / "indicadores_cardiovascular_panel_2026.csv"
SERIES_PATH = BASE_DIR / "indicadores_cardiovascular_series_2026.csv"
METADATA_PATH = BASE_DIR / "indicadores_cardiovascular_metadata_2026.json"
YEAR_COLUMNS = [2019, 2021, 2022, 2023, 2024, 2025]

STATUS_MAP = {
    "1": "Exacto",
    "2": "Exacto",
    "3": "Exacto",
    "4": "Exacto",
    "5": "No factible",
    "6": "Exacto",
    "7": "Exacto",
    "8": "Exacto",
    "9": "Exacto",
    "10": "Exacto",
    "11": "Exacto",
    "12a": "Parcial",
    "12b": "Exacto",
    "13": "Exacto",
    "14": "Exacto",
    "15": "Exacto solo 2025",
    "16": "Exacto solo 2025",
    "17": "Exacto solo 2025",
    "18": "Factible con egresos",
    "19": "Factible con egresos",
    "20": "Factible con egresos",
    "21": "Factible con egresos",
    "22": "No factible",
}

SOURCE_MAP = {
    "1": "REM P4 + PIV",
    "2": "REM P4",
    "3": "REM P4 + PIV",
    "4": "REM P4",
    "5": "Fuente externa HEARTS",
    "6": "REM P4 + PIV",
    "7": "REM P4",
    "8": "REM P4 + PIV",
    "9": "REM P4",
    "10": "REM P4",
    "11": "REM P4",
    "12a": "REM P4 (parcial)",
    "12b": "REM P4",
    "13": "REM P4",
    "14": "REM P4",
    "15": "REM P4 2025",
    "16": "REM P4 / planilla",
    "17": "REM P4 / planilla",
    "18": "Egresos hospitalarios + FONASA",
    "19": "Egresos hospitalarios + FONASA",
    "20": "Egresos hospitalarios + FONASA",
    "21": "Egresos hospitalarios + FONASA",
    "22": "Egresos hospitalarios + FONASA",
}


def group_for(indicator_id: str) -> str:
    if indicator_id in {"1", "2", "3", "4", "5"}:
        return "HTA y HEARTS"
    if indicator_id in {"6", "7", "8", "9", "10", "11", "12a", "12b"}:
        return "DM2 y seguimiento"
    if indicator_id in {"13", "14", "15"}:
        return "Función renal y ERC"
    if indicator_id in {"16", "17"}:
        return "ECV y prevención secundaria"
    return "Egresos hospitalarios"


def sort_key(indicator_id: str) -> float:
    if indicator_id.endswith("a"):
        return float(indicator_id[:-1]) + 0.1
    if indicator_id.endswith("b"):
        return float(indicator_id[:-1]) + 0.2
    return float(indicator_id)


def normalize_indicator_id(raw_id: object, indicator_name: str) -> str | None:
    if pd.isna(raw_id):
        return None

    raw_text = str(raw_id).strip()
    lower_name = indicator_name.lower()

    if raw_text == "12":
        if "tamizaje" in lower_name:
            return "12a"
        if "fondo de ojo" in lower_name:
            return "12b"

    try:
        return str(int(float(raw_text)))
    except ValueError:
        return None


def latest_available_value(row: pd.Series) -> tuple[int | None, object]:
    for year in reversed(YEAR_COLUMNS):
        value = row.get(year)
        if pd.notna(value) and str(value).strip() not in {"", "S/D"}:
            return year, value
    return None, None


def main() -> None:
    if not WORKBOOK_PATH.exists():
        raise FileNotFoundError(f"No se encontró la planilla: {WORKBOOK_PATH}")

    raw = pd.read_excel(WORKBOOK_PATH, sheet_name="Indicadores")

    panel_rows: list[dict[str, object]] = []
    notes: list[str] = []

    for _, row in raw.iterrows():
        raw_id = row["Unnamed: 0"]
        indicator_name = "" if pd.isna(row.get("Nombre del indicador")) else str(row["Nombre del indicador"]).strip()
        indicator_id = normalize_indicator_id(raw_id, indicator_name)

        if indicator_id is None:
            if pd.notna(raw_id):
                notes.append(str(raw_id).strip())
            continue

        latest_year, latest_value = latest_available_value(row)
        series_values = {f"valor_{year}": row.get(year) for year in YEAR_COLUMNS}

        panel_rows.append(
            {
                "orden": sort_key(indicator_id),
                "indicador_id": indicator_id,
                "indicador_numero_base": str(raw_id).strip(),
                "nombre_indicador": indicator_name,
                "grupo_indicador": group_for(indicator_id),
                "fuente_principal": SOURCE_MAP.get(indicator_id, ""),
                "estado_local": STATUS_MAP.get(indicator_id, ""),
                "numerador": "" if pd.isna(row.get("Numerador")) else str(row.get("Numerador")).strip(),
                "denominador": "" if pd.isna(row.get("Denominador")) else str(row.get("Denominador")).strip(),
                "amplificador": row.get("Amplificador"),
                **series_values,
                "valor_2024_rm": row.get("2024 RM"),
                "numerador_2024_rm": row.get("N"),
                "denominador_2024_rm": row.get("D"),
                "ultimo_ano_disponible": latest_year,
                "ultimo_valor_disponible": latest_value,
            }
        )

    panel = pd.DataFrame(panel_rows).sort_values("orden").reset_index(drop=True)

    series_rows: list[dict[str, object]] = []
    for _, row in panel.iterrows():
        for year in YEAR_COLUMNS:
            value = row[f"valor_{year}"]
            series_rows.append(
                {
                    "indicador_id": row["indicador_id"],
                    "nombre_indicador": row["nombre_indicador"],
                    "grupo_indicador": row["grupo_indicador"],
                    "ano": year,
                    "valor": value,
                    "valor_disponible": pd.notna(value) and str(value).strip() not in {"", "S/D"},
                }
            )

    series = pd.DataFrame(series_rows)

    panel.to_csv(PANEL_PATH, index=False, encoding="utf-8-sig")
    series.to_csv(SERIES_PATH, index=False, encoding="utf-8-sig")
    METADATA_PATH.write_text(
        json.dumps(
            {
                "archivo_origen": str(WORKBOOK_PATH),
                "notas_planilla": notes,
                "anios_series": YEAR_COLUMNS,
                "indicadores": panel["indicador_id"].tolist(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Panel generado: {PANEL_PATH}")
    print(f"Series generadas: {SERIES_PATH}")
    print(f"Metadata generada: {METADATA_PATH}")
    print(f"Indicadores procesados: {len(panel)}")


if __name__ == "__main__":
    main()
