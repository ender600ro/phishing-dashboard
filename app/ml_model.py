# app/ml_model.py
from pathlib import Path
from typing import Optional
from joblib import load
from threading import Lock

_MODEL = None
_LOCK = Lock()
MODEL_PATH = Path("models/ml_model.joblib")

def _load_model():
    global _MODEL
    if _MODEL is None and MODEL_PATH.exists():
        _MODEL = load(MODEL_PATH)

def predict_phishing_proba(text: str) -> Optional[float]:
    """
    Returns probability that the input is phishing (0..1), or None if no model.
    """
    with _LOCK:
        _load_model()
        model = _MODEL
    if model is None:
        return None
    # For empty text, return a neutral-ish probability
    if not (text and text.strip()):
        return 0.5
    proba = model.predict_proba([text])[0]
    # Find the index for class "phishing"
    classes = list(model.classes_)
    if "phishing" in classes:
        idx = classes.index("phishing")
        return float(proba[idx])
    # Fallback if labels are reversed
    return float(proba.max())
