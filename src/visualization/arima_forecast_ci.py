import warnings
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path

warnings.filterwarnings("ignore")

DATA = Path("data/processed/airport_month_features_clean.csv")
OUT_DIR = Path("reports/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "avg_delay"

CANDIDATES = [
    ((0, 1, 1), "arima_011"),
    ((1, 1, 0), "arima_110"),
    ((1, 1, 1), "arima_111"),
]

def pick_best_order(series: pd.Series):
    """Choose best ARIMA order using last-point validation."""
    train = series.iloc[:-1]
    actual = float(series.iloc[-1])

    best = None
    best_err = float("inf")

    for order, name in CANDIDATES:
        try:
            model = SARIMAX(
                train.astype(float),
                order=order,
                seasonal_order=(0, 0, 0, 0),
                trend="n",
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            res = model.fit(disp=False, maxiter=200)
            pred = float(res.forecast(steps=1).iloc[0])
            err = abs(actual - pred)
            if err < best_err:
                best_err = err
                best = (order, name)
        except Exception:
            continue

    if best is None:
        raise RuntimeError("All ARIMA candidates failed.")
    return best

def plot_forecast_with_ci(airport: str, horizon: int = 3, last_n: int = 10, save: bool = True):
    df = pd.read_csv(DATA, parse_dates=["date"]).sort_values(["airport", "date"])
    sub = df[df["airport"].str.upper() == airport.upper()].sort_values("date")

    if sub.empty:
        raise ValueError(f"Airport not found: {airport}")

    y = sub[TARGET].astype(float)
    dates = sub["date"]

    # Pick best order, then refit on full series
    order, name = pick_best_order(y)

    model = SARIMAX(
        y,
        order=order,
        seasonal_order=(0, 0, 0, 0),
        trend="n",
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    res = model.fit(disp=False, maxiter=200)

    fc = res.get_forecast(steps=horizon)
    mean = fc.predicted_mean
    ci = fc.conf_int(alpha=0.05)  # 95% CI
    lower = ci.iloc[:, 0]
    upper = ci.iloc[:, 1]

    # Build forecast dates: next month begins
    last_date = dates.max()
    fc_dates = pd.date_range(
        start=last_date + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq="MS"
    )

    # Plot last N points + forecast
    tail = sub.tail(min(last_n, len(sub)))

    plt.figure(figsize=(9, 4.5))
    plt.plot(tail["date"], tail[TARGET], marker="o", label="Actual")
    plt.plot(fc_dates, mean.values, marker="o", label=f"Forecast ({name})")
    plt.fill_between(fc_dates, lower.values, upper.values, alpha=0.2, label="95% CI")

    plt.title(f"Avg Delay Forecast with 95% CI — {airport.upper()} ({name})")
    plt.xlabel("Month")
    plt.ylabel("Average Delay (minutes)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    if save:
        out = OUT_DIR / f"forecast_ci_{airport.upper().replace(' ', '_').replace('(', '').replace(')', '')}.png"
        plt.savefig(out, dpi=180)
        print("Saved:", out)

    plt.show()

if __name__ == "__main__":
    plot_forecast_with_ci("ABERDEEN", horizon=3)
