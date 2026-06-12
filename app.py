from __future__ import annotations

from pathlib import Path

import pandas as pd


MONTHS = {
    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12,
}


DOWNLOADS = Path.home() / "Downloads"
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "macro_indonesia_sample.csv"


def extract_inflation() -> pd.DataFrame:
    rows: list[dict] = []
    files = sorted(DOWNLOADS.glob("Inflasi Bulanan (M-to-M), *.xlsx"))
    for path in files:
        raw = pd.read_excel(path, header=None)
        year_values = raw.iloc[2].dropna().astype(str).str.extract(r"(\d{4})").dropna()
        if year_values.empty:
            continue
        year = int(year_values.iloc[0, 0])
        indonesia = raw[raw[0].astype(str).str.upper().str.strip().eq("INDONESIA")]
        if indonesia.empty:
            continue
        values = indonesia.iloc[0, 1:13]
        for month_name, month_num in MONTHS.items():
            value = pd.to_numeric(values.iloc[month_num - 1], errors="coerce")
            if pd.notna(value):
                rows.append(
                    {
                        "year": year,
                        "month_num": month_num,
                        "month": month_name,
                        "inflation_mtm": float(value),
                    }
                )
    return pd.DataFrame(rows)


def extract_bi_rate() -> pd.DataFrame:
    matches = list(DOWNLOADS.glob("bi_rate_combined_cleaned*.csv"))
    if not matches:
        return pd.DataFrame(columns=["year", "month_num", "bi_rate"])
    df = pd.read_csv(matches[0])
    df["month_num"] = df["Month"].map(MONTHS)
    return df.rename(columns={"Year": "year", "BI_Rate": "bi_rate"})[["year", "month_num", "bi_rate"]]


def main() -> None:
    inflation = extract_inflation()
    bi_rate = extract_bi_rate()
    merged = inflation.merge(bi_rate, on=["year", "month_num"], how="left")
    merged = merged.sort_values(["year", "month_num"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(merged)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
