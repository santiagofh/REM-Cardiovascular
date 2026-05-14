from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

REGION_RM = "13"
PREVISION_FONASA = "1"
PLANILLA_DENOMINADOR = 5_108_594

AGE_GROUPS_GRANULAR = [
    "15 A 19 AÑOS", "20 A 24 AÑOS", "25 A 29 AÑOS",
    "30 A 34 AÑOS", "35 A 39 AÑOS", "40 A 44 AÑOS",
    "45 A 49 AÑOS", "50 A 54 AÑOS", "55 A 59 AÑOS",
    "60 A 64 AÑOS", "65 A 69 AÑOS", "70 A 74 AÑOS",
    "75 A 79 AÑOS", "80 A 84 AÑOS", "85 A MAS",
]

AGE_GROUPS_DECENNIAL = [
    "10 a 19", "20 a 29", "30 a 39",
    "40 a 49", "50 a 59", "60 a 69",
    "70 a 79", "80 a 89", "90 y más",
]

INDICADORES_EGRESOS = [
    {"id": 18, "nombre": "Enfermedad cerebrovascular",
     "cie_codes": ["G45", "I63", "I64", "I65", "I66", "I67", "I69"], "factor": 10_000},
    {"id": 19, "nombre": "Enfermedades isquémicas del corazón",
     "cie_codes": ["I20", "I21", "I22", "I23", "I24", "I25"], "factor": 10_000},
    {"id": 20, "nombre": "Insuficiencia cardíaca",
     "cie_codes": ["I50", "J81"], "factor": 10_000},
    {"id": 21, "nombre": "Diabetes mellitus",
     "cie_codes": ["E11", "E12", "E13", "E14"], "factor": 10_000},
    {"id": 22, "nombre": "Amputación pie diabético (proxy)",
     "cie_codes": ["E105", "E115", "E145"], "factor": 10_000},
]

FILE_NAMES = {
    2020: "EGRE_DATOS_ABIERTOS_2020.csv",
    2021: "EGR_DATOS_ABIERTO_2021.csv",
    2022: "EGRE_DATOS_ABIERTOS_2022.csv",
    2023: "EGRESOS_2023.csv",
    2024: "EGRESOS_2024.csv",
}


def load_maestro():
    master_path = "C:/Users/fariass/OneDrive - SUBSECRETARIA DE SALUD PUBLICA/Escritorio/DATA/ESTABLECIMIENTOS/establecimientos_20260424.csv"
    master = pd.read_csv(master_path, sep=";", dtype=str,
                         usecols=["ComunaCodigo", "ComunaGlosa",
                                   "SeremiSaludCodigo_ServicioDeSaludCodigo",
                                   "SeremiSaludGlosa_ServicioDeSaludGlosa"])
    master = master.drop_duplicates(subset=["ComunaCodigo"]).copy()
    master["ComunaCodigo"] = master["ComunaCodigo"].astype(str).str.strip()
    master = master[master["ComunaCodigo"] != ""]
    return master.rename(columns={
        "ComunaCodigo": "IdComuna", "ComunaGlosa": "comuna_nombre",
        "SeremiSaludCodigo_ServicioDeSaludCodigo": "IdServicio",
        "SeremiSaludGlosa_ServicioDeSaludGlosa": "servicio_salud",
    })


def get_age_groups(year: int) -> list[str]:
    return AGE_GROUPS_GRANULAR if year in (2021, 2024) else AGE_GROUPS_DECENNIAL


def col_name(ind_id: int) -> str:
    return f"ind_{ind_id}"


def main():
    maestro = load_maestro()
    all_rows = []

    for year, fname in FILE_NAMES.items():
        path = ROOT / f"EGRESOS_{year}" / fname
        if not path.exists():
            print(f"[{year}] Archivo no encontrado, saltando...")
            continue

        age_groups = get_age_groups(year)
        print(f"[{year}] Procesando {fname}...")

        chunks = []

        for chunk in pd.read_csv(path, sep=";", encoding="latin1",
                                 usecols=["REGION_RESIDENCIA", "PREVISION",
                                          "GRUPO_EDAD", "DIAG1", "COMUNA_RESIDENCIA"],
                                 chunksize=500_000):
            for col in ["REGION_RESIDENCIA", "PREVISION", "GRUPO_EDAD", "COMUNA_RESIDENCIA", "DIAG1"]:
                chunk[col] = chunk[col].astype(str).str.strip()

            mask = (
                chunk["REGION_RESIDENCIA"].eq(REGION_RM)
                & chunk["PREVISION"].eq(PREVISION_FONASA)
                & chunk["GRUPO_EDAD"].isin(age_groups)
            )
            f = chunk[mask].copy()
            if f.empty:
                continue

            for ind in INDICADORES_EGRESOS:
                f[col_name(ind["id"])] = match_codes(f["DIAG1"], ind["cie_codes"])

            chunks.append(f[["COMUNA_RESIDENCIA"] + [col_name(i["id"]) for i in INDICADORES_EGRESOS]])

        if not chunks:
            print(f"  Sin registros FONASA RM 15+")
            continue

        df = pd.concat(chunks, ignore_index=True)

        by_comuna = df.groupby("COMUNA_RESIDENCIA", as_index=False)[
            [col_name(i["id"]) for i in INDICADORES_EGRESOS]
        ].sum()

        total_rm_v = by_comuna[[col_name(i["id"]) for i in INDICADORES_EGRESOS]].sum()

        for _, row in by_comuna.iterrows():
            comuna = row["COMUNA_RESIDENCIA"]
            comuna_nombre = "Desconocido"
            servicio = "Desconocido"
            id_servicio = ""
            m = maestro[maestro["IdComuna"] == comuna]
            if not m.empty:
                comuna_nombre = m.iloc[0]["comuna_nombre"]
                servicio = m.iloc[0]["servicio_salud"]
                id_servicio = m.iloc[0]["IdServicio"]
            for ind in INDICADORES_EGRESOS:
                n = int(row[col_name(ind["id"])])
                tasa = round((n / PLANILLA_DENOMINADOR) * ind["factor"], 4)
                all_rows.append({
                    "Ano": year, "IdComuna": comuna, "comuna_nombre": comuna_nombre,
                    "IdServicio": id_servicio, "servicio_salud": servicio,
                    "indicador_id": ind["id"], "indicador_nombre": ind["nombre"],
                    "n_egresos": n, "denominador": PLANILLA_DENOMINADOR, "tasa_x10000": tasa,
                })

        for ind in INDICADORES_EGRESOS:
            n = int(total_rm_v[col_name(ind["id"])])
            tasa = round((n / PLANILLA_DENOMINADOR) * ind["factor"], 4)
            all_rows.append({
                "Ano": year, "IdComuna": "13", "comuna_nombre": "RM Total",
                "IdServicio": "13", "servicio_salud": "RM",
                "indicador_id": ind["id"], "indicador_nombre": ind["nombre"],
                "n_egresos": n, "denominador": PLANILLA_DENOMINADOR, "tasa_x10000": tasa,
            })

        n_total = int(total_rm_v.sum())
        print(f"  {len(by_comuna)} comunas, {n_total:,} egresos matching indicadores")

    if not all_rows:
        print("No hay resultados.")
        return

    df_out = pd.DataFrame(all_rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "indicadores_egresos_hospitalarios_detalle.csv"
    df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGuardado: {out_path}")
    print(f"Filas: {len(df_out):,}")


def match_codes(series: pd.Series, codes: list[str]) -> pd.Series:
    mask = pd.Series(False, index=series.index)
    for code in codes:
        if len(code) == 3:
            mask |= series.str.startswith(code, na=False)
        else:
            mask |= series == code
    return mask


if __name__ == "__main__":
    main()
