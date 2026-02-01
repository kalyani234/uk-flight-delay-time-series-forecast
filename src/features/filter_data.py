import pandas as pd
from pathlib import Path

INP = Path("data/processed/airport_month_features_clean.csv")
OUT = Path("data/processed/airport_month_features_filtered.csv")

MIN_MONTHS_PER_AIRPORT = 6

# What models need to safely train:
REQUIRED_FOR_MODELING = [
    "avg_delay",
    "ontime_pct",
    "cancelled_pct",
    "total_flights",
    "month",
    "year",
    "avg_delay_lag_1",
    "avg_delay_lag_3",
    "ontime_pct_lag_1",
    "ontime_pct_lag_3",
    "cancelled_pct_lag_1",
    "cancelled_pct_lag_3",
]

def main():
    df = pd.read_csv(INP, parse_dates=["date"])

    # 1) Keep airports with enough history (ARIMA stability)
    counts = df.groupby("airport").size()
    keep = counts[counts >= MIN_MONTHS_PER_AIRPORT].index
    df = df[df["airport"].isin(keep)].copy()

    # 2) Drop rows that are not model-ready (missing lags / features)
    # This removes early months where lag_1 / lag_3 are NaN.
    df = df.dropna(subset=REQUIRED_FOR_MODELING)

    # Sort for reproducibility
    df = df.sort_values(["airport", "date"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print("✅ FILTERED (MODEL-READY) DATASET CREATED")
    print("Saved:", OUT)
    print("Rows:", len(df), "Airports:", df["airport"].nunique(), "Months:", df["date"].nunique())

if __name__ == "__main__":
    main()
