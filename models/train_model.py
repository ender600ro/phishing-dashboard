# train_model.py
# Baseline text classifier for phishing vs. legit emails.
# - Uses a tiny fallback dataset so you can verify end-to-end immediately.
# - If data/labeled_emails.csv exists (columns: text,label), it will use that instead.

from pathlib import Path
import json
import sys
from typing import List, Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from joblib import dump

DATA_CSV = Path("data/labeled_emails.csv")
MODEL_PATH = Path("models/ml_model.joblib")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

def tiny_fallback() -> pd.DataFrame:
    # Very small mixed set to prove the pipeline works.
    phishing: List[str] = [
        "Urgent action required verify your account now click here to avoid suspension",
        "Security alert your password will expire login and confirm immediately",
        "Your package is on hold pay customs fee here http://malicious-pay.com",
        "We detected unusual activity reset your login now",
        "Invoice overdue click here to pay"
    ]
    legit: List[str] = [
        "Team meeting moved to Tuesday please see agenda attached",
        "Your Amazon order has shipped tracking details inside",
        "Monthly newsletter new features and updates",
        "Thanks for your message I will get back to you tomorrow",
        "Reminder project review on Friday afternoon"
    ]
    texts = phishing + legit
    labels = ["phishing"] * len(phishing) + ["legit"] * len(legit)
    return pd.DataFrame({"text": texts, "label": labels})

def load_dataset() -> pd.DataFrame:
    if DATA_CSV.exists():
        df = pd.read_csv(DATA_CSV)
        assert {"text","label"}.issubset(df.columns), "CSV must have columns: text,label"
        return df.dropna(subset=["text","label"]).reset_index(drop=True)
    return tiny_fallback()

def train(df: pd.DataFrame) -> Tuple[Pipeline, dict]:
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1, max_df=0.95)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))
    ])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, list(pipe.classes_).index("phishing")]
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary", pos_label="phishing")
    cm = confusion_matrix(y_test, y_pred, labels=["legit","phishing"]).tolist()

    metrics = {
        "accuracy": round(float(acc), 3),
        "precision_phishing": round(float(prec), 3),
        "recall_phishing": round(float(rec), 3),
        "f1_phishing": round(float(f1), 3),
        "classes": list(pipe.classes_),
        "confusion_matrix_rows": ["legit","phishing"],
        "confusion_matrix": cm,
        "test_size": int(len(y_test))
    }
    return pipe, metrics

def main():
    df = load_dataset()
    print(f"[INFO] Dataset size: {len(df)} rows (labels: {df['label'].value_counts().to_dict()})")

    model, metrics = train(df)
    dump(model, MODEL_PATH)
    print(f"[OK] Saved model to {MODEL_PATH}")

    with open(REPORT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("[METRICS]", json.dumps(metrics, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[ERROR]", e)
        sys.exit(1)
