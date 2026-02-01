"""
api/main.py

FastAPI service for UK flight delay forecasting.

Design choices:
- Uses CLEAN dataset for /airports, /forecast, /plots
- Enforces ARIMA eligibility per airport inside endpoints (>= MIN_HISTORY_POINTS)
- ARIMA: best-of-3 candidate selection per airport using last-point validation
- Returns forecast mean + 95% confidence interval
- /plots returns a PNG generated with matplotlib (Agg backend for Docker/macOS)
- Serves saved report PNGs from /reports/figures/*
- Lists available saved figures via /report-figures
- Forecast calls are logged to Postgres (best-effort; DB failure won't break API)

Run (local):
  uvicorn api.main:app --reload

Run (module):
  python -m uvicorn api.main:app --reload
"""

import os
import io
import warnings
from typing import Tuple
from pathlib import Path
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Headless backend for server environments (Docker/macOS safe)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa: E402

from api.db import init_db, log_forecast  # noqa: E402
from api.schemas import AirportsResponse, ForecastResponse  # noqa: E402

warnings.filterwarnings("ignore")


# =========================
# Config (from env)
# =========================
DATA_PATH = os.getenv("DATA_PATH", "data/processed/airport_month_features_clean.csv")
TARGET = os.getenv("TARGET", "avg_delay")
MIN_HISTORY_POINTS = int(os.getenv("MIN_HISTORY_POINTS", "6"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")

# Best-of-3 ARIMA candidates (p,d,q) + readable name
CANDIDATES = [
    ((0, 1, 1), "arima_011"),
    ((1, 1, 0), "arima_110"),
    ((1, 1, 1), "arima_111"),
]


# =========================
# Lifespan (startup/shutdown)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB init (best-effort)
    try:
        init_db()
        print("✅ DB initialized")
    except Exception as e:
        print(f"⚠️ DB init failed (continuing): {e}")

    yield

    # Optional shutdown hook
    print("🛑 API shutdown")


app = FastAPI(
    title="UK Flight Delay Forecast API (ARIMA + CI)",
    version="0.1.0",
    lifespan=lifespan,
)

# Ensure figures folder exists + expose as static
FIG_DIR = Path(os.getenv("FIG_DIR", "reports/figures"))
FIG_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/reports/figures", StaticFiles(directory=str(FIG_DIR)), name="figures")

# CORS (React dev + optionally others)
origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data once
if not Path(DATA_PATH).exists():
    raise RuntimeError(
        f"DATA_PATH not found: {DATA_PATH}. "
        "Build features first or set DATA_PATH env var."
    )

df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values(["airport", "date"])
AIRPORTS = sorted(df["airport"].dropna().unique().tolist())


# =========================
# Helpers
# =========================
def resolve_order(model_name: str) -> Tuple[int, int, int]:
    """Map model name -> ARIMA order tuple."""
    for order, name in CANDIDATES:
        if name == model_name:
            return order
    raise ValueError(f"Unknown model name: {model_name}")


def fit_arima(series: pd.Series, order: Tuple[int, int, int]):
    """Fit SARIMAX (non-seasonal ARIMA) model."""
    model = SARIMAX(
        series.astype(float),
        order=order,
        seasonal_order=(0, 0, 0, 0),
        trend="n",
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False, maxiter=200)


def choose_best_model_name(series: pd.Series) -> str:
    """
    Choose best ARIMA candidate using last-point validation:
    - Fit on series[:-1]
    - Predict 1 step
    - Pick smallest abs error vs series[-1]
    """
    series = series.dropna().astype(float).reset_index(drop=True)
    if len(series) < MIN_HISTORY_POINTS:
        raise ValueError(
            f"Not enough history for ARIMA (need >= {MIN_HISTORY_POINTS} points)."
        )

    train = series.iloc[:-1]
    actual = float(series.iloc[-1])

    best_err = float("inf")
    best_name = None

    for order, name in CANDIDATES:
        try:
            res = fit_arima(train, order)
            pred_1 = float(res.forecast(steps=1).iloc[0])
            err = abs(actual - pred_1)
            if err < best_err:
                best_err = err
                best_name = name
        except Exception:
            continue

    if best_name is None:
        raise RuntimeError("All ARIMA candidates failed for this airport.")
    return best_name


def get_airport_df(airport: str) -> pd.DataFrame:
    """Return airport subset sorted by date (case-insensitive match)."""
    sub = df[df["airport"].str.upper() == airport.upper()].sort_values("date")
    if sub.empty:
        raise HTTPException(status_code=404, detail="Airport not found. Use /airports.")
    return sub


def compute_forecast(sub: pd.DataFrame, horizon: int):
    """Core forecast logic reused by /forecast and /plots."""
    series = sub[TARGET].dropna().astype(float)
    last_date = sub["date"].max()

    model_used = choose_best_model_name(series)
    order = resolve_order(model_used)

    res = fit_arima(series, order)
    fc = res.get_forecast(steps=horizon)

    mean = fc.predicted_mean
    ci = fc.conf_int(alpha=0.05)  # 95% CI

    return model_used, last_date, mean, ci


# =========================
# Endpoints
# =========================
@app.get("/health")
def health():
    return {"status": "ok", "rows": int(len(df)), "airports": int(len(AIRPORTS))}


@app.get("/airports", response_model=AirportsResponse)
def airports():
    return AirportsResponse(airports=AIRPORTS)


@app.get("/forecast", response_model=ForecastResponse)
def forecast(
    airport: str = Query(..., description="Airport name, e.g. ABERDEEN"),
    horizon: int = Query(1, ge=1, le=3, description="Months ahead to forecast (1–3)"),
):
    sub = get_airport_df(airport)

    try:
        model_used, last_date, mean, ci = compute_forecast(sub, horizon)

        # Use last step (horizon-th month) as the "headline" forecast
        pred = float(mean.iloc[-1])
        lower_95 = float(ci.iloc[-1, 0])
        upper_95 = float(ci.iloc[-1, 1])

        forecast_month = (last_date + pd.offsets.MonthBegin(horizon)).date()

        # Best-effort logging (DB downtime should not break API)
        try:
            log_forecast(
                airport=airport.upper(),
                last_observed_month=last_date.date(),
                forecast_month=forecast_month,
                horizon=horizon,
                model_used=model_used,
                predicted=round(pred, 2),
                lower_95=round(lower_95, 2),
                upper_95=round(upper_95, 2),
            )
        except Exception as log_err:
            print(f"⚠️ DB logging failed: {log_err}")

        return ForecastResponse(
            airport=airport.upper(),
            last_observed_month=last_date.date(),
            forecast_month=forecast_month,
            horizon=horizon,
            predicted_avg_delay_minutes=round(pred, 2),
            lower_95=round(lower_95, 2),
            upper_95=round(upper_95, 2),
            model_used=model_used,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {e}")


@app.get(
    "/plots",
    responses={200: {"content": {"image/png": {}}}},
)
def plots(
    airport: str = Query(..., description="Airport name, e.g. ABERDEEN"),
    horizon: int = Query(2, ge=1, le=3, description="Months ahead (1–3)"),
):
    sub = get_airport_df(airport)

    try:
        model_used, last_date, mean, ci = compute_forecast(sub, horizon)

        # future months start at next month begin
        fc_dates = pd.date_range(
            start=last_date + pd.offsets.MonthBegin(1),
            periods=horizon,
            freq="MS",
        )

        # Plot last N actual points for readability
        tail = sub.tail(min(12, len(sub)))

        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(tail["date"], tail[TARGET], marker="o", label="Actual")
        ax.plot(fc_dates, mean.values, marker="o", label=f"Forecast ({model_used})")
        ax.fill_between(fc_dates, ci.iloc[:, 0], ci.iloc[:, 1], alpha=0.25, label="95% CI")

        ax.set_title(
            f"Avg Delay Forecast with 95% CI — {airport.upper()} ({model_used})"
        )
        ax.set_xlabel("Month")
        ax.set_ylabel("Average Delay (minutes)")
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200)
        plt.close(fig)
        buf.seek(0)

        return Response(content=buf.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plot generation failed: {e}")


@app.get("/report-figures")
def report_figures():
    """Lists saved PNGs in reports/figures (generated by visualization scripts)."""
    files = sorted([p.name for p in FIG_DIR.glob("*.png")])
    return {"files": files}
