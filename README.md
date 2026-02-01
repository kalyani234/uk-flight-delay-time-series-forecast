# ✈️ UK Flight Delay Forecasting System

An end-to-end data science and engineering project that forecasts **average flight delays for UK airports** using historical aviation performance data.  
The system demonstrates the complete lifecycle from **raw data processing** to **forecasting, visualisation, API deployment, and frontend integration**.

---

## 🔍 Project Overview

- Processes monthly UK Civil Aviation Authority (CAA) airport data  
- Builds clean and model-ready datasets  
- Forecasts average flight delays **1–3 months ahead** using ARIMA  
- Generates analytical and forecasting visualisations  
- Exposes results via a FastAPI backend and React frontend  

Result:

[!VideoRecording](https://github.com/user-attachments/assets/98bdc64a-52fb-46ba-b332-dc3127e46f64)
---

## 🎯 Use Cases (3)

- **Delay Forecasting** – Predict future average delays for UK airports  
- **Operational Insights** – Identify airports with higher delay risk  
- **Portfolio Project** – Demonstrates ML, APIs, Docker, and frontend integration  

---

## 🧰 Tech Stack

| Layer | Technologies |
|------|-------------|
| Frontend | React, Vite, CSS |
| Backend | FastAPI, Python |
| Modelling | ARIMA (statsmodels), XGBoost |
| Data Processing | pandas, NumPy |
| Visualisation | Matplotlib |
| Database | PostgreSQL |
| DevOps | Docker, Docker Compose |

---

## 🔄 Project Flow

1. Raw airport performance data is ingested from Excel files  
2. Data is cleaned, standardised, and enriched with time-based features  
3. Airports with insufficient history are filtered for modelling  
4. Models (Baseline, ARIMA, XGBoost) are trained and evaluated  
5. Visualisations and forecast plots are generated and saved  
6. FastAPI serves forecasts, plots, and reports  
7. React UI allows interactive exploration  


---

## 📁 Project Structure

```
UK-FLIGHT-DELAY-FORECAST/
├── .venv/                      # local virtualenv (git ignored)
├── Dockerfile                  # builds FastAPI + ML pipeline image
├── requirements.txt            # pandas, statsmodels, xgboost, fastapi, matplotlib, psycopg2, etc.
├── README.md
│
├── api/                        # FastAPI backend
│   ├── main.py                 # app entrypoint + endpoints (/forecast, /plots, /airports, /health)
│   ├── schemas.py              # Pydantic models for responses
│   └── db.py                   # PostgreSQL logging (optional, graceful degradation)
│
├── infra/                      # deployment & startup logic
│   ├── .env                    # DB credentials, paths (never committed)
│   ├── docker-compose.yml      # api + postgres services
│   └── entrypoint.sh           # runs full ML pipeline before starting uvicorn
│
├── src/                        # core data science code
│   ├── features/
│   │   ├── build_features.py   # raw → cleaned dataset + lags
│   │   └── filter_data.py      # keeps airports with enough history
│   │
│   ├── models/
│   │   ├── config.py           # paths, constants
│   │   ├── train_baseline.py   # lag-1 naive forecast
│   │   ├── train_sarima.py     # best ARIMA per airport
│   │   ├── train_xgb.py        # XGBoost with features
│   │   ├── run_all.py          # trains everything in sequence
│   │   └── save_scores.py      # saves MAE comparison
│   │
│   ├── eval/
│   │   └── backtest.py         # rolling forecast evaluation
│   │
│   └── visualization/
│       ├── generate_all.py     # runs all plots
│       ├── arima_forecast_ci.py  # main forecast plot + CI
│       ├── plot_*              # heatmap, trends, top airports, relationships, baseline comparison…
│       └── utils.py            # safe savefig helpers
│
├── data/
│   ├── raw/                    # original CAA monthly Excel files
│   └── processed/              # cleaned + filtered Parquet/CSV
│
├── reports/
│   └── figures/                # all saved PNG charts (forecasts + analytics)
│
└── frontend/                   # React + Vite dashboard
├── src/
└── vite.config.js
```

--- 


---

## ▶️ Run with Docker (Recommended)

```bash
docker compose -f infra/docker-compose.yml up --build
```
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Frontend: http://localhost:5173
- All pipelines (features, models, visualisations) run automatically on startup.


## ▶️ Run Locally (Without Docker)

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m src.features.build_features
python -m src.features.filter_data
python -m src.models.run_all
python -m src.visualization.generate_all

uvicorn api.main:app --reload
```

### Use Cases

- Flight Delay Forecasting – Predict average flight delays for UK airports 1–3 months ahead using historical performance data.

- Operational Planning – Help airlines and airport operators anticipate high-delay periods and plan staffing, gates, and resources accordingly.

- Performance Analysis – Analyse relationships between on-time performance, cancellations, and delays across airports and months.

- Data Visualisation & Reporting – Generate and store reusable charts and forecasts for reporting and trend analysis.

- Decision Support – Support data-driven decisions for scheduling, capacity planning, and service reliability improvements.

- Portfolio Demonstration – Showcase an end-to-end time series forecasting system with data pipelines, modelling, APIs, visualisations, Docker, and a React frontend.


---

## Final Notes

Built as a portfolio-ready project to showcase applied data science, time-series forecasting, and full-stack ML system design.
 
---
