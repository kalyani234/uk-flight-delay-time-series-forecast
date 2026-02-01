import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.utils import save_fig
import matplotlib
matplotlib.use("Agg")  # ✅ Docker/headless safe



DATA = "data/processed/airport_month_features_clean.csv"

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    pivot = df.pivot_table(index="airport", columns="date", values="avg_delay", aggfunc="mean")

    # Sort airports by overall mean delay
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    plt.figure(figsize=(12, 7))
    plt.imshow(pivot.values, aspect="auto")
    plt.title("Average Delay Heatmap (Airport × Month)")
    plt.xlabel("Month")
    plt.ylabel("Airport")

    plt.xticks(range(len(pivot.columns)), [d.strftime("%Y-%m") for d in pivot.columns], rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)

    plt.colorbar(label="Avg Delay (minutes)")
    save_fig("heatmap_avg_delay_airport_month")
    plt.close()

if __name__ == "__main__":
    main()
