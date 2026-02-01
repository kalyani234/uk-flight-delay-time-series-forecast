import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.utils import save_fig
import matplotlib
matplotlib.use("Agg")  # ✅ Docker/headless safe



DATA = "data/processed/airport_month_features_clean.csv"

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    d = df.dropna(subset=["avg_delay", "avg_delay_lag_1"]).copy()

    plt.figure(figsize=(6.5, 6))
    plt.scatter(d["avg_delay_lag_1"], d["avg_delay"], alpha=0.8)
    plt.title("Actual vs Baseline (Lag-1) Avg Delay")
    plt.xlabel("Lag-1 Avg Delay (minutes)")
    plt.ylabel("Actual Avg Delay (minutes)")
    plt.tight_layout()

    save_fig("scatter_actual_vs_lag1_baseline")
    plt.close()


if __name__ == "__main__":
    main()
