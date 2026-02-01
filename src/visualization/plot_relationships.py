import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.utils import save_fig
import matplotlib
matplotlib.use("Agg")  # ✅ Docker/headless safe


DATA = "data/processed/airport_month_features_clean.csv"

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])

    # cancellations vs delay
    plt.figure(figsize=(7, 5))
    plt.scatter(df["cancelled_pct"], df["avg_delay"])
    plt.title("Cancellations % vs Avg Delay")
    plt.xlabel("Cancelled %")
    plt.ylabel("Avg Delay (minutes)")
    plt.tight_layout()
    save_fig("scatter_cancelled_vs_delay")

    # punctuality vs delay
    plt.figure(figsize=(7, 5))
    plt.scatter(df["ontime_pct"], df["avg_delay"])
    plt.title("On-time % (<15 mins) vs Avg Delay")
    plt.xlabel("On-time %")
    plt.ylabel("Avg Delay (minutes)")
    plt.tight_layout()
    save_fig("scatter_ontime_vs_delay")
    plt.close()


if __name__ == "__main__":
    main()
