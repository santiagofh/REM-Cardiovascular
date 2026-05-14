from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
VALIDACION_PATH = BASE_DIR / "indicadores_cardiovascular_validacion_rm_2024.csv"


def _locale_decimal(value: float, decimals: int = 2) -> str:
    sign = "-" if value < 0 else ""
    formatted = f"{abs(value):.{decimals}f}"
    int_part, dec_part = formatted.split(".")
    int_part = f"{int(int_part):,}".replace(",", ".")
    return f"{sign}{int_part},{dec_part}"


def main():
    if not VALIDACION_PATH.exists():
        print(f"Archivo no encontrado: {VALIDACION_PATH}")
        return

    df = pd.read_csv(VALIDACION_PATH, dtype={"indicador_id": str})
    numeric_cols = [
        "Ano", "numerador", "denominador",
        "valor_calculado_pct", "valor_referencia_2024_rm_proporcion", "diferencia_pp",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    rows = []
    for _, row in df.iterrows():
        estado = row["estado_calculo"]
        estado_label = "Calculado" if estado == "calculado" else "Proxy"

        calc = row["valor_calculado_pct"]
        ref = row["valor_referencia_2024_rm_proporcion"]
        diff = row["diferencia_pp"]

        ref_pct = ref * 100 if pd.notna(ref) else None

        rows.append({
            "Indicador": f"{row['indicador_id']}. {row['nombre_indicador']}",
            "Estado": estado_label,
            "Valor calculado RM 2024": _locale_decimal(calc, 2) + "%" if pd.notna(calc) else "",
            "Valor planilla RM 2024": _locale_decimal(ref_pct, 2) + "%" if ref_pct is not None else "",
            "Numerador": f"{int(row['numerador']):,}".replace(",", ".") if pd.notna(row['numerador']) else "",
            "Denominador": f"{int(row['denominador']):,}".replace(",", ".") if pd.notna(row['denominador']) else "",
            "Diferencia (pp)": f"{'+' if diff > 0 else ''}{_locale_decimal(diff, 3)} pp" if pd.notna(diff) else "",
        })

    out = pd.DataFrame(rows)
    out_path = BASE_DIR.parent / "comparacion.xlsx"
    out.to_excel(out_path, index=False, sheet_name="Validacion RM 2024")
    print(f"Guardado: {out_path}")
    print(f"Filas: {len(out)}")


if __name__ == "__main__":
    main()
