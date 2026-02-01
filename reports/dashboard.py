from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA = "data/processed/airport_month_features_clean.csv"
OUTDIR = Path("reports/figures")
OUTDIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(DATA, parse_dates=["date"]).sort_values(["airport","date"])

    # 1) Avg delay trend for top-5 busiest airports (latest month)
    last = df["date"].max()
    busiest = (
        df[df["date"] == last]
        .sort_values("total_flights", ascending=False)
        .head(5)["airport"]
        .tolist()
    )

    fig, ax = plt.subplots(figsize=(10,5))
    for a in busiest:
        s = df[df["airport"] == a]
        ax.plot(s["date"], s["avg_delay"], marker="o", label=a)
    ax.set_title("Avg Delay Trend — Top 5 Busiest Airports")
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg Delay (minutes)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTDIR / "trend_top5_busiest.png", dpi=200)
    plt.close(fig)

    # 2) Latest month ranking (bar chart)
    latest = df[df["date"] == last].sort_values("avg_delay", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(latest["airport"], latest["avg_delay"])
    ax.set_title(f"Top 10 Airports by Avg Delay — {last.date()}")
    ax.set_xlabel("Airport")
    ax.set_ylabel("Avg Delay (minutes)")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(OUTDIR / "top10_avg_delay_latest.png", dpi=200)
    plt.close(fig)

    print("✅ Saved figures to:", OUTDIR)

if __name__ == "__main__":
    main()
