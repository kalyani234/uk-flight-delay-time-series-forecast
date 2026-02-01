import csv
import json
from pathlib import Path

METRICS_FILES = [
    Path("data/processed/metrics_baseline.json"),
    Path("data/processed/metrics_xgb.json"),
    Path("data/processed/metrics_arima.json"),
]

OUT = Path("data/processed/model_scores.csv")


def main():
    rows = []
    missing = []

    for p in METRICS_FILES:
        if not p.exists():
            missing.append(str(p))
            continue

        m = json.loads(p.read_text())
        rows.append([m["model"], m["metric"], float(m["value"])])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "metric", "value"])
        for r in rows:
            w.writerow([r[0], r[1], f"{r[2]:.6f}"])

    print("✅ Saved:", OUT)
    if missing:
        print("⚠️ Missing metrics files (run training first):")
        for x in missing:
            print("-", x)


if __name__ == "__main__":
    main()
