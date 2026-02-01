"""
src/visualization/generate_all.py

Runs all visualization modules and saves PNGs into reports/figures/.
Designed to be safe for Docker startup: continues even if one plot fails.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "src.visualization.plot_top_airports",
    "src.visualization.plot_delay_heatmap",
    "src.visualization.plot_multi_trends",
    "src.visualization.plot_baseline_scatter",
    "src.visualization.plot_relationships",
    "src.visualization.arima_forecast_ci",
]

FIG_DIR = Path("reports/figures")


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    ok, failed = 0, []

    for m in SCRIPTS:
        print("\n==============================")
        print("RUN:", m)
        print("==============================")

        try:
            subprocess.run([sys.executable, "-m", m], check=True)
            ok += 1
        except subprocess.CalledProcessError as e:
            failed.append((m, e.returncode))
            print(f"⚠️ Failed: {m} (exit code {e.returncode}) — continuing...")

    print("\n✅ Figures folder:", FIG_DIR.resolve())
    print(f"✅ Success: {ok}/{len(SCRIPTS)}")
    if failed:
        print("⚠️ Failed modules:")
        for name, code in failed:
            print(f" - {name} (code {code})")

    # Do NOT raise at the end — keep Docker startup stable.


if __name__ == "__main__":
    main()
