"""
build_features.py

Purpose (CLEAN stage):
- Convert messy monthly CAA Excel reports into a single canonical, analysis-ready dataset.
- Standardise schema + types + time index.
- Create time features and lag features BUT do NOT remove early months just because lags are missing.
  (Model eligibility filtering belongs in filter_data.py)

Why we ignore "Run Date":
- Some CAA months include a "Run Date" column (publication timestamp).
- It is metadata (when report was generated), not when flights happened.
- Using it as a feature risks leakage and does not represent the reporting period.
"""

from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/xlsx")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# In CAA "On Time Performance Tables.xlsx", the header row is typically on the 3rd row (0-indexed = 2)
HEADER_ROW_INDEX = 2

# Canonical schema: we only keep the columns we need for forecasting
# Extra columns (e.g. "Run Date", "... Same Month Previous Year") are intentionally ignored.
CANONICAL_COLUMNS = {
    "Reporting Period": "period",
    "Reporting Airport": "airport",
    "Flights on time (<15mins) Percent": "ontime_pct",
    "Average Delay Minutes": "avg_delay",
    "Flights Cancelled Percent": "cancelled_pct",
    "Total Flights": "total_flights",
}

CORE_REQUIRED = ["period", "airport", "ontime_pct", "avg_delay", "cancelled_pct", "total_flights"]


def load_one_file(path: Path) -> pd.DataFrame:
    """
    Read a single XLSX and return only the canonical columns, renamed.
    We read sheet_name="Airport" because that's where the airport-level table is.
    """
    df = pd.read_excel(path, sheet_name="Airport", header=HEADER_ROW_INDEX)

    # Guardrail: fail fast if the expected schema isn't present (prevents silent bad parsing)
    missing = [c for c in CANONICAL_COLUMNS.keys() if c not in df.columns]
    if missing:
        raise ValueError(
            f"{path.name}: Missing expected columns: {missing}. "
            f"Check HEADER_ROW_INDEX or the sheet layout."
        )

    # Keep only the columns we want (ignore Run Date / previous year columns etc.)
    df = df[list(CANONICAL_COLUMNS.keys())].rename(columns=CANONICAL_COLUMNS)
    return df


def load_all_files() -> pd.DataFrame:
    """
    Load all XLSX files and concatenate into one dataframe.
    """
    frames = []
    for p in sorted(RAW_DIR.glob("*.xlsx")):
        frames.append(load_one_file(p))

    if not frames:
        raise RuntimeError("No XLSX files found in data/raw/xlsx/")

    return pd.concat(frames, ignore_index=True)


def clean_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert data types to ensure downstream modelling works:
    - period -> string, date -> datetime (Reporting Period is the time axis)
    - numeric fields -> float (strip commas like '2,448')
    - airport -> clean string
    """
    df["period"] = df["period"].astype(str).str.strip()

    # Reporting Period is the correct time axis (e.g., 202506)
    df["date"] = pd.to_datetime(df["period"], format="%Y%m", errors="coerce")

    numeric_cols = ["ontime_pct", "avg_delay", "cancelled_pct", "total_flights"]
    for c in numeric_cols:
        df[c] = (
            df[c]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["airport"] = df["airport"].astype(str).str.strip()
    return df


def remove_non_airports(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove aggregate rows like 'All Airports' which are not real airports.
    Keeping them can distort per-airport modelling and comparisons.
    """
    return df[df["airport"].str.lower() != "all airports"]


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple calendar features.
    Useful for ML models and plots, and safe (no leakage).
    """
    df = df.sort_values(["airport", "date"])
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    return df


def add_lags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create lag features per airport.
    IMPORTANT: early months will have NaN lags; we keep them in the CLEAN dataset.
    Filtering for model-readiness happens later in filter_data.py.
    """
    for col in ["avg_delay", "ontime_pct", "cancelled_pct"]:
        df[f"{col}_lag_1"] = df.groupby("airport")[col].shift(1)
        df[f"{col}_lag_3"] = df.groupby("airport")[col].shift(3)
    return df


def main():
    df = load_all_files()
    df = clean_types(df)
    df = remove_non_airports(df)

    # Drop rows only if core values are missing (NOT lag columns)
    df = df.dropna(subset=CORE_REQUIRED + ["date"])

    # De-duplicate in case the same airport-month appears twice
    df = df.drop_duplicates(subset=["airport", "date"])

    df = add_time_features(df)
    df = add_lags(df)

    out = OUT_DIR / "airport_month_features_clean.csv"
    df.to_csv(out, index=False)

    print("✅ CLEAN DATASET CREATED")
    print("Saved:", out)
    print("Rows:", len(df))
    print("Airports:", df["airport"].nunique())
    print("Months:", df["date"].nunique())
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
