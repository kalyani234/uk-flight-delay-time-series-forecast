import os
from datetime import datetime
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5432/flights")
engine = create_engine(DB_URL, future=True)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS forecast_logs (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            airport TEXT NOT NULL,
            last_observed_month DATE NOT NULL,
            forecast_month DATE NOT NULL,
            horizon INT NOT NULL,
            model_used TEXT NOT NULL,
            predicted DOUBLE PRECISION NOT NULL,
            lower_95 DOUBLE PRECISION,
            upper_95 DOUBLE PRECISION
        );
        """))

def log_forecast(
    airport: str,
    last_observed_month,
    forecast_month,
    horizon: int,
    model_used: str,
    predicted: float,
    lower_95: float | None = None,
    upper_95: float | None = None,
):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO forecast_logs
        (created_at, airport, last_observed_month, forecast_month, horizon, model_used, predicted, lower_95, upper_95)
        VALUES
        (:created_at, :airport, :lom, :fm, :h, :m, :p, :l, :u)
        """), {
            "created_at": datetime.utcnow(),
            "airport": airport,
            "lom": last_observed_month,
            "fm": forecast_month,
            "h": horizon,
            "m": model_used,
            "p": predicted,
            "l": lower_95,
            "u": upper_95,
        })
