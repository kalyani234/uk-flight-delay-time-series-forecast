import numpy as np
import pandas as pd
from pathlib import Path
from xgboost import XGBRegressor

DATA_PATH = "data/processed/airport_month_features_filtered.csv"
OUT_MODEL = Path("data/processed/xgb_model.json")
OUT_PREDS = Path("data/processed/xgb_predictions.csv")

FEATURES = [
    "ontime_pct",
    "cancelled_pct",
    "total_flights",
    "month",
    "avg_delay_lag_1",
    "avg_delay_lag_3",
    "ontime_pct_lag_1",
    "ontime_pct_lag_3",
    "cancelled_pct_lag_1",
    "cancelled_pct_lag_3",
]

def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values(["airport", "date"])
    last_month = df["date"].max()

    train = df[df["date"] < last_month].dropna(subset=FEATURES + ["avg_delay"])
    test = df[df["date"] == last_month].dropna(subset=FEATURES + ["avg_delay"])

    X_train, y_train = train[FEATURES], train["avg_delay"].astype(float)
    X_test, y_test = test[FEATURES], test["avg_delay"].astype(float)

    model = XGBRegressor(
        n_estimators=400,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = float(np.mean(np.abs(y_test.values - preds)))

    OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(OUT_MODEL))

    out = test[["airport", "date", "avg_delay"]].copy()
    out["pred_avg_delay"] = preds
    out.to_csv(OUT_PREDS, index=False)

    print(f"✅ XGBoost MAE (last month holdout): {mae:.4f}")
    print(f"Saved model: {OUT_MODEL}")
    print(f"Saved predictions: {OUT_PREDS}")

if __name__ == "__main__":
    main()
