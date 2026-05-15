from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\REM\REM-Cardiovascular"
)
EGRESOS_2024_PATH = Path(r"D:\DATA\EGRESOS_HOSPITALARIOS_C\EH_2024.csv")
BENEF_2024_PATH = Path(
    r"C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\FONASA\Poblacion fonasa inscrita x comuna\BENEFICIARIOS\Beneficiarios_RM_2024.xlsx"
)

USECOLS = [
    "REGION",
    "PREVI",
    "TIPO_EDAD",
    "EDAD_CANT",
    "ServicioSalud",
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


def beneficiaries_15_plus_2024() -> dict[str, int]:
    raw = pd.read_excel(BENEF_2024_PATH, sheet_name="Benef SS-Sex-Edad 2024", header=None)
    cols = ["territorio", "total"] + list(range(0, 91)) + ["si"]
    df = raw.iloc[6:].copy().reset_index(drop=True)
    df = df.iloc[:, : len(cols)]
    df.columns = cols
    region_row = df.iloc[0]
    return {
        "total_beneficiarios": int(pd.to_numeric(region_row["total"], errors="coerce")),
        "edad_15_89": int(pd.to_numeric(region_row[list(range(15, 90))], errors="coerce").fillna(0).sum()),
        "edad_15_90": int(pd.to_numeric(region_row[list(range(15, 91))], errors="coerce").fillna(0).sum()),
        "edad_15_89_mas_si": int(
            pd.to_numeric(region_row[list(range(15, 90))], errors="coerce").fillna(0).sum()
            + pd.to_numeric(region_row["si"], errors="coerce")
        ),
        "edad_15_90_mas_si": int(
            pd.to_numeric(region_row[list(range(15, 91))], errors="coerce").fillna(0).sum()
            + pd.to_numeric(region_row["si"], errors="coerce")
        ),
    }


def any_match(df: pd.DataFrame, columns: list[str], pattern: str) -> pd.Series:
    return pd.concat([df[col].astype(str).str.match(pattern, na=False) for col in columns], axis=1).any(axis=1)


def diabetes_any_position(df: pd.DataFrame) -> pd.Series:
    return any_match(df, DIAG_COLS, r"^E1[0-4]")


def load_filtered_egresos_2024() -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        EGRESOS_2024_PATH,
        sep=";",
        encoding="latin1",
        usecols=USECOLS,
        dtype=str,
        chunksize=300_000,
        low_memory=False,
    ):
        for col in USECOLS:
            chunk[col] = chunk[col].astype(str).str.strip()

        mask = (
            chunk["REGION"].eq("13")
            & chunk["PREVI"].isin(["01", "1"])
            & chunk["TIPO_EDAD"].eq("1")
            & pd.to_numeric(chunk["EDAD_CANT"], errors="coerce").ge(15)
        )
        subset = chunk[mask].copy()
        if not subset.empty:
            chunks.append(subset)

    if not chunks:
        return pd.DataFrame(columns=USECOLS)

    return pd.concat(chunks, ignore_index=True)


def main() -> None:
    benef = beneficiaries_15_plus_2024()
    egresos = load_filtered_egresos_2024()
    diabetes_any = diabetes_any_position(egresos)

    variants = {
        "diag1_proc_ppal_1701": egresos["DIAG1"].str.match(r"^E1[0-4]", na=False)
        & egresos["PROCED_PPAL"].str.match(r"^1701", na=False),
        "diag_any_proc_any_1701": diabetes_any & any_match(egresos, PROC_COLS, r"^1701"),
        "diag_any_int_any_18": diabetes_any & any_match(egresos, INT_COLS, r"^18"),
        "diag_any_int_any_17_o_18": diabetes_any & any_match(egresos, INT_COLS, r"^(17|18)"),
        "diag_any_proc1701_o_int_17_18": diabetes_any
        & (any_match(egresos, PROC_COLS, r"^1701") | any_match(egresos, INT_COLS, r"^(17|18)")),
        "diag_any_set_amplio": diabetes_any
        & (
            any_match(egresos, PROC_COLS, r"^1701")
            | any_match(egresos, INT_COLS, r"^(1703|1704|1802|1803|1902)")
        ),
    }

    rows: list[dict[str, object]] = []
    for name, mask in variants.items():
        n = int(mask.sum())
        rows.append(
            {
                "escenario": name,
                "numerador": n,
                "tasa_x_10000_con_benef_15_90_mas_si": round(n / benef["edad_15_90_mas_si"] * 10000, 4),
            }
        )

    out = pd.DataFrame(rows).sort_values("numerador", ascending=False)
    print("Beneficiarios 2024")
    print(pd.Series(benef).to_string())
    print("\nEscenarios numerador 2024")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
