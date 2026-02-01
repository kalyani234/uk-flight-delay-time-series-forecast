from pathlib import Path

DATA = Path("data/processed/airport_month_features_clean.csv")
TARGET = "avg_delay"

FEATURES = [
    "month", "year",
    "avg_delay_lag_1", "avg_delay_lag_3",
    "ontime_pct_lag_1", "ontime_pct_lag_3",
    "cancelled_pct_lag_1", "cancelled_pct_lag_3",
    "total_flights",
]
