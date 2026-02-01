import numpy as np
import pandas as pd
from pathlib import Path

DATA_PATH = "data/processed/airport_month_features_filtered.csv"
OUT = Path("data/processed/baseline_backtest.csv")

def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values(["airport", "date"])

    # Baseline: predict avg_delay using lag-1 avg_delay
    df = df.dropna(subset=["avg_delay", "avg_delay_lag_1"]).copy()
    df["pred_avg_delay"] = df["avg_delay_lag_1"]

    mae = float(np.mean(np.abs(df["avg_delay"] - df["pred_avg_delay"])))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out = df[["airport", "date", "avg_delay", "pred_avg_delay"]]
    df_out.to_csv(OUT, index=False)

    print(f"✅ Baseline MAE: {mae:.4f}")
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
