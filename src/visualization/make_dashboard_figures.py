import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from src.visualization.arima_forecast_ci import plot_forecast_with_ci
import matplotlib
matplotlib.use("Agg")  # ✅ Docker/headless safe


DATA = Path("data/processed/airport_month_features_clean.csv")
OUT_DIR = Path("reports/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save_trend(df, airport: str):
    sub = df[df["airport"].str.upper() == airport.upper()].sort_values("date")
    plt.figure(figsize=(9,4.5))
    plt.plot(sub["date"], sub["avg_delay"], marker="o")
    plt.title(f"Average Delay Over Time — {airport.upper()}")
    plt.xlabel("Month")
    plt.ylabel("Average Delay (minutes)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    out = OUT_DIR / f"trend_{airport.upper().replace(' ','_')}.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("Saved:", out)

def save_top_airports_bar(df):
    agg = df.groupby("airport")["avg_delay"].mean().sort_values(ascending=False)
    plt.figure(figsize=(9,6))
    plt.barh(agg.index, agg.values)
    plt.title("Average Delay by Airport (Mean)")
    plt.xlabel("Average Delay (minutes)")
    plt.tight_layout()
    out = OUT_DIR / "avg_delay_by_airport.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("Saved:", out)

def save_scatter(df):
    plt.figure(figsize=(7.5,5))
    plt.scatter(df["ontime_pct"], df["avg_delay"])
    plt.title("Punctuality vs Average Delay")
    plt.xlabel("On-time % (<15 mins)")
    plt.ylabel("Average Delay (minutes)")
    plt.tight_layout()
    out = OUT_DIR / "scatter_punctuality_vs_delay.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("Saved:", out)

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    airport = "ABERDEEN"

    save_trend(df, airport)
    save_top_airports_bar(df)
    save_scatter(df)
    plot_forecast_with_ci(airport, horizon=3)

    print("\n✅ Dashboard figures saved to reports/figures/")

if __name__ == "__main__":
    main()
