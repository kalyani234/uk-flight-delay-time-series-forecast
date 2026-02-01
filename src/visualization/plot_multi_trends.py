import pandas as pd
import matplotlib.pyplot as plt
from src.visualization.utils import save_fig
import matplotlib
matplotlib.use("Agg")  # ✅ Docker/headless safe



DATA = "data/processed/airport_month_features_clean.csv"

AIRPORTS = [
    "ABERDEEN",
    "HEATHROW",
    "GATWICK",
    "MANCHESTER",
    "EDINBURGH",
]

def main():
    df = pd.read_csv(DATA, parse_dates=["date"]).sort_values("date")

    plt.figure(figsize=(10, 5.5))
    for a in AIRPORTS:
        sub = df[df["airport"].str.upper() == a].sort_values("date")
        if len(sub) == 0:
            continue
        plt.plot(sub["date"], sub["avg_delay"], marker="o", label=a)

    plt.title("Avg Delay Trends (Selected Airports)")
    plt.xlabel("Month")
    plt.ylabel("Avg Delay (minutes)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    save_fig("multi_airport_delay_trends")
    plt.close()


if __name__ == "__main__":
    main()
