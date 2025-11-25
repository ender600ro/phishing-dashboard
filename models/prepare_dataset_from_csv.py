# prepare_dataset_from_csv.py
from pathlib import Path
import pandas as pd
import re
import csv

SRC = Path("data/Phishing_Email.csv")
OUT = Path("data/labeled_emails.csv")

POS_PAT = re.compile(r"(phish|spam|malicious|fraud|scam|attack)", re.I)
NEG_PAT = re.compile(r"(legit|ham|benign|clean|safe|normal|not\s*phish)", re.I)

def normalize_label(s):
    if pd.isna(s): 
        return None
    v = str(s).strip().lower()
    if POS_PAT.search(v): 
        return "phishing"
    if NEG_PAT.search(v): 
        return "legit"
    if v in {"1","true"}: 
        return "phishing"
    if v in {"0","false"}: 
        return "legit"
    return None  # unknown -> drop (we can extend if needed)

def main():
    if not SRC.exists():
        raise SystemExit(f"[ERROR] {SRC} not found")
    df = pd.read_csv(SRC)
    # Expect exact columns
    if not {"Email Text","Email Type"}.issubset(df.columns):
        raise SystemExit(f"[ERROR] Need columns 'Email Text' and 'Email Type'. Found: {list(df.columns)}")
    df = df.rename(columns={"Email Text":"text","Email Type":"label"})
    df["text"]  = df["text"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    df["label"] = df["label"].map(normalize_label)

    # Keep only valid, non-empty texts
    df = df.dropna(subset=["text","label"])
    df = df[df["text"].str.len() >= 10].reset_index(drop=True)

    counts = df["label"].value_counts().to_dict()
    print("[INFO] Counts after mapping:", counts)
    if not counts:
        print("[HINT] Labels weren’t recognized. Run the probe command I gave to see exact label strings, then tell me the values.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"[OK] Wrote {OUT} ({len(df)} rows). Next: python train_model.py")

if __name__ == "__main__":
    main()
