#!/usr/bin/env bash
set -e

echo "✅ Container starting..."

# Optional pipeline toggle (default ON)
if [ "${RUN_PIPELINE:-1}" = "1" ]; then
  echo "✅ Running full pipeline before starting API..."

  # 1) Build features
  python -m src.features.build_features
  python -m src.features.filter_data

  # 2) Train models (won't block startup if optional deps missing)
  python -m src.models.run_all || true

  # 3) Generate all visualisations (won't block startup)
  python -m src.visualization.generate_all || true

  echo "✅ Pipeline complete."
else
  echo "ℹ️ RUN_PIPELINE=0, skipping pipeline."
fi

echo "✅ Starting API..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
