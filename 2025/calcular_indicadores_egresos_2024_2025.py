from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
EGRESOS_DIR = Path("D:/DATA/EGRESOS_HOSPITALARIOS_C")
BENEFICIARIOS_PATH = BASE_DIR / "beneficiarios_fonasa_15_mas_rm_comuna_2024_2025.csv"

REGION_RM = "13"

INDICADORES = [
    {
        "id": "18",
        "nombre": "Tasa de egresos hospitalarios por enfermedad cerebrovascular",
        "cie": ["G45", "I63", "I64", "I65", "I66", "I67", "I69"],
    },
    {
        "id": "19",
        "nombre": "Tasa de egresos hospitalarios por enfermedades isquémicas del corazón",
        "cie": ["I20", "I21", "I22", "I23", "I24", "I25"],
    },
    {
        "id": "20",
        "nombre": "Tasa de egresos hospitalarios por insuficiencia cardíaca",
        "cie": ["I50", "J81"],
    },
    {
        "id": "21",
        "nombre": "Tasa de egresos hospitalarios por diabetes mellitus",
        "cie": ["E11", "E12", "E13", "E14"],
    },
    {
        "id": "22",
        "nombre": "Tasa de egresos hospitalarios por amputación extremidad inferior en diabetes",
        "cie": [],
    },
]

FILE_NAMES = {
    2024: "EH_2024.csv",
    2025: "EH_2025_preliminar.csv",
}

USECOLS = [
    "REGION",
    "PREVI",
    "TIPO_EDAD",
    "EDAD_CANT",
    "COMUNA",
    "DIAG1",
    "DIAG2",
    "DIAG3",
    "DIAG4",
    "DIAG5",
    "DIAG6",
    "DIAG7",
    "DIAG8",
    "DIAG9",
    "DIAG10",
    "DIAG11",
    "INTERV_Q",
    "INTERV_Q_PPAL",
    "INTERV_Q_2",
    "INTERV_Q_3",
    "PROCED",
    "PROCED_PPAL",
    "PROCED_2",
    "PROCED_3",
]

DIAG_COLS = [
    "DIAG1",
    "DIAG2",
    "DIAG3",
    "DIAG4",
    "DIAG5",
    "DIAG6",
    "DIAG7",
    "DIAG8",
    "DIAG9",
    "DIAG10",
    "DIAG11",
]
INT_COLS = ["INTERV_Q", "INTERV_Q_PPAL", "INTERV_Q_2", "INTERV_Q_3"]
PROC_COLS = ["PROCED", "PROCED_PPAL", "PROCED_2", "PROCED_3"]


def _match_codes(series: pd.Series, codes: list[str]) -> pd.Series:
    mask = pd.Series(False, index=series.index)
    for code in codes:
        mask |= series.astype(str).str.match(r"^" + code, na=False)
    return mask


def _any_match(df: pd.DataFrame, columns: list[str], pattern: str) -> pd.Series:
    return pd.concat(
        [df[col].astype(str).str.match(pattern, na=False) for col in columns],
        axis=1,
    ).any(axis=1)


def _match_amputation(df: pd.DataFrame) -> pd.Series:
    diabetes_any = _any_match(df, DIAG_COLS, r"^E1[0-4]")
    amputation_proc = _any_match(df, PROC_COLS, r"^1701")
    amputation_interv = _any_match(df, INT_COLS, r"^(1703|1704|1802|1803|1902)")
    return diabetes_any & (amputation_proc | amputation_interv)


def load_beneficiarios():
    beneficiarios = pd.read_csv(BENEFICIARIOS_PATH, dtype=str)
    beneficiarios["Ano"] = pd.to_numeric(beneficiarios["Ano"], errors="coerce")
    beneficiarios["beneficiarios_fonasa_15_mas"] = pd.to_numeric(
        beneficiarios["beneficiarios_fonasa_15_mas"], errors="coerce"
    )
    beneficiarios["IdComuna"] = beneficiarios["IdComuna"].astype(str).str.strip()
    beneficiarios["IdServicio"] = beneficiarios["IdServicio"].astype(str).str.strip()
    beneficiarios["servicio_salud"] = beneficiarios["servicio_salud"].astype(str).str.strip()
    beneficiarios["comuna"] = beneficiarios["comuna"].astype(str).str.strip()
    return beneficiarios


def main():
    beneficiarios = load_beneficiarios()

    beneficiarios_comuna = (
        beneficiarios.groupby(["Ano", "IdComuna", "IdServicio", "servicio_salud", "comuna"])["beneficiarios_fonasa_15_mas"]
        .sum()
        .reset_index()
    )

    beneficiarios_ss = (
        beneficiarios_comuna.groupby(["Ano", "IdServicio", "servicio_salud"])["beneficiarios_fonasa_15_mas"]
        .sum()
        .reset_index()
    )

    beneficiarios_rm = (
        beneficiarios_comuna.groupby(["Ano"])["beneficiarios_fonasa_15_mas"].sum().reset_index()
    )

    all_rows = []

    for year, fname in FILE_NAMES.items():
        path = EGRESOS_DIR / fname
        if not path.exists():
            print(f"[{year}] Archivo no encontrado: {path}")
            continue

        print(f"[{year}] Procesando {fname}...")
        chunks_by_comuna: list[pd.DataFrame] = []
        total_rows = 0

        for chunk in pd.read_csv(
            path, sep=";", encoding="latin1",
            usecols=USECOLS, chunksize=500_000, dtype=str,
        ):
            for col in USECOLS:
                chunk[col] = chunk[col].astype(str).str.strip()

            mask = (
                chunk["REGION"].eq(REGION_RM)
                & chunk["PREVI"].isin(["01", "1"])
                & chunk["TIPO_EDAD"].eq("1")
                & pd.to_numeric(chunk["EDAD_CANT"], errors="coerce").ge(15)
            )
            f = chunk[mask].copy()
            if f.empty:
                continue

            total_rows += len(f)

            for ind in INDICADORES:
                if ind["id"] == "22":
                    f[ind["id"]] = _match_amputation(f)
                else:
                    f[ind["id"]] = _match_codes(f["DIAG1"], ind["cie"])

            cols = ["COMUNA"] + [ind["id"] for ind in INDICADORES]
            agg = f[cols].groupby("COMUNA").sum().reset_index()
            chunks_by_comuna.append(agg)

        if not chunks_by_comuna:
            print(f"  Sin registros FONASA RM 15+")
            continue

        comuna_agg = pd.concat(chunks_by_comuna, ignore_index=True)
        comuna_agg = comuna_agg.groupby("COMUNA")[[ind["id"] for ind in INDICADORES]].sum().reset_index()
        comuna_totals = comuna_agg.set_index("COMUNA").to_dict(orient="index")

        # Comuna-level rows
        beneficiarios_c_year = beneficiarios_comuna[beneficiarios_comuna["Ano"] == year]
        for comuna, counts in comuna_totals.items():
            benef_row = beneficiarios_c_year[beneficiarios_c_year["IdComuna"] == comuna]
            denom = int(benef_row["beneficiarios_fonasa_15_mas"].sum()) if not benef_row.empty else 0
            for ind in INDICADORES:
                n = int(counts.get(ind["id"], 0))
                tasa = round((n / denom) * 10_000, 4) if denom > 0 else 0.0
                all_rows.append({
                    "Ano": year,
                    "indicador_id": ind["id"],
                    "nombre_indicador": ind["nombre"],
                    "nivel": "comuna",
                    "IdServicio": benef_row.iloc[0]["IdServicio"] if not benef_row.empty else "",
                    "servicio_salud": benef_row.iloc[0]["servicio_salud"] if not benef_row.empty else "",
                    "comuna": comuna,
                    "n_egresos": n,
                    "denominador_fonasa_15_mas": denom,
                    "tasa_x10000": tasa,
                })

        # SS-level rows (aggregate from comuna totals)
        beneficiarios_ss_year = beneficiarios_ss[beneficiarios_ss["Ano"] == year]
        ss_egresos: dict[str, dict[str, int]] = {}
        for comuna, counts in comuna_totals.items():
            benef_row = beneficiarios_c_year[beneficiarios_c_year["IdComuna"] == comuna]
            if benef_row.empty:
                continue
            ss_id = benef_row.iloc[0]["IdServicio"]
            if ss_id not in ss_egresos:
                ss_egresos[ss_id] = {ind["id"]: 0 for ind in INDICADORES}
            for ind in INDICADORES:
                ss_egresos[ss_id][ind["id"]] += int(counts.get(ind["id"], 0))

        for _, benef_row in beneficiarios_ss_year.iterrows():
            ss_id = benef_row["IdServicio"]
            denom = int(benef_row["beneficiarios_fonasa_15_mas"])
            counts = ss_egresos.get(ss_id, {})
            for ind in INDICADORES:
                n = counts.get(ind["id"], 0)
                tasa = round((n / denom) * 10_000, 4) if denom > 0 else 0.0
                all_rows.append({
                    "Ano": year,
                    "indicador_id": ind["id"],
                    "nombre_indicador": ind["nombre"],
                    "nivel": "servicio_salud",
                    "IdServicio": ss_id,
                    "servicio_salud": benef_row["servicio_salud"],
                    "comuna": "",
                    "n_egresos": n,
                    "denominador_fonasa_15_mas": denom,
                    "tasa_x10000": tasa,
                })

        # RM-level rows (aggregate from comuna totals)
        rm_benef_row = beneficiarios_rm[beneficiarios_rm["Ano"] == year]
        rm_denom = int(rm_benef_row["beneficiarios_fonasa_15_mas"].sum()) if not rm_benef_row.empty else 0
        rm_counts = {ind["id"]: 0 for ind in INDICADORES}
        for comuna, counts in comuna_totals.items():
            for ind in INDICADORES:
                rm_counts[ind["id"]] += int(counts.get(ind["id"], 0))
        for ind in INDICADORES:
            n = rm_counts[ind["id"]]
            tasa = round((n / rm_denom) * 10_000, 4) if rm_denom > 0 else 0.0
            all_rows.append({
                "Ano": year,
                "indicador_id": ind["id"],
                "nombre_indicador": ind["nombre"],
                "nivel": "rm",
                "IdServicio": "",
                "servicio_salud": "",
                "comuna": "",
                "n_egresos": n,
                "denominador_fonasa_15_mas": rm_denom,
                "tasa_x10000": tasa,
            })

        print(f"  RM FONASA 15+ (egresos observados): {total_rows:,} | {len(comuna_totals)} comunas")
        print(f"  RM beneficiarios FONASA 15+ (denominador): {rm_denom:,}")
        for ind in INDICADORES:
            print(f"  Ind {ind['id']}: {rm_counts[ind['id']]:,} egresos")

    if not all_rows:
        print("No hay resultados.")
        return

    out = pd.DataFrame(all_rows)
    out_path = BASE_DIR / "indicadores_egresos_rm_2024_2025.csv"
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGuardado: {out_path}")
    print(f"Filas: {len(out):,}")
    print(f"Niveles: {out['nivel'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
