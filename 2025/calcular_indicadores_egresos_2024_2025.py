from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
EGRESOS_DIR = Path("D:/DATA/EGRESOS_HOSPITALARIOS_C")

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

USECOLS = ["REGION", "PREVI", "TIPO_EDAD", "EDAD_CANT", "DIAG1", "PROCED_PPAL", "COMUNA"]


def _match_codes(series: pd.Series, codes: list[str]) -> pd.Series:
    mask = pd.Series(False, index=series.index)
    for code in codes:
        mask |= series.astype(str).str.match(r"^" + code, na=False)
    return mask


def _match_amputation(diag1: pd.Series, proc: pd.Series) -> pd.Series:
    return diag1.astype(str).str.match(r"^E1[0-4]", na=False) & proc.astype(str).str.match(r"^1701", na=False)


def load_piv():
    piv_path = BASE_DIR / "poblacion_inscrita_validada_15_mas_rm_establecimiento_2023_2025.csv"
    piv = pd.read_csv(piv_path, dtype=str)
    piv["AnoIndicador"] = pd.to_numeric(piv["AnoIndicador"], errors="coerce")
    piv["poblacion_inscrita_validada_15_mas"] = pd.to_numeric(piv["poblacion_inscrita_validada_15_mas"], errors="coerce")
    piv["IdComuna_master"] = piv["IdComuna_master"].astype(str).str.strip()
    piv["IdServicio_master"] = piv["IdServicio_master"].astype(str).str.strip()
    piv["servicio_salud_master"] = piv["servicio_salud_master"].astype(str).str.strip()
    return piv


def main():
    piv = load_piv()

    # Aggregate PIV by comuna (per year)
    piv_comuna = (
        piv.groupby(["AnoIndicador", "IdComuna_master", "IdServicio_master", "servicio_salud_master"])["poblacion_inscrita_validada_15_mas"]
        .sum()
        .reset_index()
        .rename(columns={"IdComuna_master": "comuna", "IdServicio_master": "IdServicio", "servicio_salud_master": "servicio_salud"})
    )
    piv_comuna["comuna"] = piv_comuna["comuna"].astype(str).str.strip()

    # Aggregate PIV by servicio de salud
    piv_ss = piv_comuna.groupby(["AnoIndicador", "IdServicio", "servicio_salud"])["poblacion_inscrita_validada_15_mas"].sum().reset_index()

    # Aggregate PIV RM total
    piv_rm = piv_comuna.groupby(["AnoIndicador"])["poblacion_inscrita_validada_15_mas"].sum().reset_index()

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
                    f[ind["id"]] = _match_amputation(f["DIAG1"], f["PROCED_PPAL"])
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
        piv_c_year = piv_comuna[piv_comuna["AnoIndicador"] == year]
        for comuna, counts in comuna_totals.items():
            piv_row = piv_c_year[piv_c_year["comuna"] == comuna]
            denom = int(piv_row["poblacion_inscrita_validada_15_mas"].sum()) if not piv_row.empty else 0
            for ind in INDICADORES:
                n = int(counts.get(ind["id"], 0))
                tasa = round((n / denom) * 10_000, 4) if denom > 0 else 0.0
                all_rows.append({
                    "Ano": year,
                    "indicador_id": ind["id"],
                    "nombre_indicador": ind["nombre"],
                    "nivel": "comuna",
                    "IdServicio": piv_row.iloc[0]["IdServicio"] if not piv_row.empty else "",
                    "servicio_salud": piv_row.iloc[0]["servicio_salud"] if not piv_row.empty else "",
                    "comuna": comuna,
                    "n_egresos": n,
                    "denominador_piv": denom,
                    "tasa_x10000": tasa,
                })

        # SS-level rows (aggregate from comuna totals)
        piv_ss_year = piv_ss[piv_ss["AnoIndicador"] == year]
        ss_egresos: dict[str, dict[str, int]] = {}
        for comuna, counts in comuna_totals.items():
            piv_row = piv_c_year[piv_c_year["comuna"] == comuna]
            if piv_row.empty:
                continue
            ss_id = piv_row.iloc[0]["IdServicio"]
            if ss_id not in ss_egresos:
                ss_egresos[ss_id] = {ind["id"]: 0 for ind in INDICADORES}
            for ind in INDICADORES:
                ss_egresos[ss_id][ind["id"]] += int(counts.get(ind["id"], 0))

        for _, piv_row in piv_ss_year.iterrows():
            ss_id = piv_row["IdServicio"]
            denom = int(piv_row["poblacion_inscrita_validada_15_mas"])
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
                    "servicio_salud": piv_row["servicio_salud"],
                    "comuna": "",
                    "n_egresos": n,
                    "denominador_piv": denom,
                    "tasa_x10000": tasa,
                })

        # RM-level rows (aggregate from comuna totals)
        rm_piv_row = piv_rm[piv_rm["AnoIndicador"] == year]
        rm_denom = int(rm_piv_row["poblacion_inscrita_validada_15_mas"].sum()) if not rm_piv_row.empty else 0
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
                "denominador_piv": rm_denom,
                "tasa_x10000": tasa,
            })

        print(f"  RM FONASA 15+: {total_rows:,} | {len(comuna_totals)} comunas")
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
