from pathlib import Path
import re

OUT_DIR = Path("reports/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def safe_name(s: str) -> str:
    s = s.upper()
    s = re.sub(r"[^A-Z0-9_]+", "_", s)
    return s.strip("_")

def save_fig(name: str, dpi: int = 200):
    import matplotlib.pyplot as plt
    path = OUT_DIR / f"{name}.png"
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print("Saved:", path)
