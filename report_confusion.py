# report_confusion.py
from pathlib import Path
import json
import matplotlib.pyplot as plt

REPORT = Path("reports/metrics.json")
OUT = Path("reports/confusion_matrix.png")

def main():
    data = json.loads(REPORT.read_text())
    cm = data["confusion_matrix"]
    rows = data["confusion_matrix_rows"]  # ["legit","phishing"]

    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_xticks([0,1]); ax.set_xticklabels(rows, rotation=15)
    ax.set_yticks([0,1]); ax.set_yticklabels(rows)

    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i][j], ha="center", va="center", fontsize=12)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(OUT, dpi=160)
    print(f"[OK] Wrote {OUT}")

if __name__ == "__main__":
    main()
