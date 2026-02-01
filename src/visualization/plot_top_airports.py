import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.utils import save_fig
import matplotlib
matplotlib.use("Agg")  # ✅ Docker/headless safe


DATA = "data/processed/airport_month_features_clean.csv"

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    mean_delay = df.groupby("airport")["avg_delay"].mean().sort_values(ascending=False)

    top = mean_delay.head(15)

    plt.figure(figsize=(10, 6))
    plt.barh(top.index[::-1], top.values[::-1])
    plt.title("Top 15 Airports by Average Delay (Mean)")
    plt.xlabel("Average Delay (minutes)")
    plt.ylabel("Airport")
    plt.tight_layout()
    save_fig("top15_airports_by_avg_delay")
    plt.close()


if __name__ == "__main__":
    main()
