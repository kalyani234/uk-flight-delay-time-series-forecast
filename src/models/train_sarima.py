import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

DATA_PATH = "data/processed/airport_month_features_filtered.csv"

CANDIDATES = {
    "arima_011": (0, 1, 1),
    "arima_110": (1, 1, 0),
    "arima_111": (1, 1, 1),
}

def fit(series: pd.Series, order):
    model = SARIMAX(
        series.astype(float),
        order=order,
        seasonal_order=(0, 0, 0, 0),
        trend="n",
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False, maxiter=200)

def best_model_for_airport(series: pd.Series):
    if len(series) < 6:
        return None, None

    train = series.iloc[:-1]
    actual = float(series.iloc[-1])

    best_name, best_err = None, float("inf")
    for name, order in CANDIDATES.items():
        try:
            res = fit(train, order)
            pred = float(res.forecast(1).iloc[0])
            err = abs(actual - pred)
            if err < best_err:
                best_err = err
                best_name = name
        except Exception:
            continue

    return best_name, best_err

def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values(["airport", "date"])

    errors = []
    chosen = {k: 0 for k in CANDIDATES}

    for airport, g in df.groupby("airport"):
        series = g["avg_delay"].dropna().reset_index(drop=True)
        name, err = best_model_for_airport(series)
        if name is None:
            continue
        chosen[name] += 1
        errors.append(err)

    mae = float(np.mean(errors))
    print(f"✅ ARIMA (best-of-3) MAE (airport-wise 1-step): {mae:.4f}")
    print("Model choices:", chosen)

if __name__ == "__main__":
    main()
