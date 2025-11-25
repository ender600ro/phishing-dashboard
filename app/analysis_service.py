# app/analysis_service.py
from typing import Dict, List, Optional

def fuse_signals(
    ml_prob: Optional[float],
    vt_results: List[Optional[Dict]],
    us_results: List[Optional[Dict]],
    indicators: List[str]
) -> Dict:
    """
    Combine ML probability (0..1) + VirusTotal + urlscan signals into a single score.
    Simple, explainable rules for a first pass.
    """

    # Base score from ML (neutral if missing)
    score = float(ml_prob) if (ml_prob is not None) else 0.30
    reasons: List[str] = []
    tags: List[str] = []

    # ---------------------------
    # VirusTotal weighting
    # ---------------------------
    vt_mal = sum((r or {}).get("malicious", 0) for r in vt_results if r)
    vt_seen = any((r or {}).get("seen", False) for r in vt_results if r)

    if vt_mal > 0:
        score += 0.25
        reasons.append(f"VirusTotal: {vt_mal} malicious finding(s)")
        tags.append("vt:malicious")
    elif vt_seen:
        score -= 0.05
        reasons.append("VirusTotal: known, not flagged malicious")
        tags.append("vt:seen")

    # ---------------------------
    # urlscan.io weighting
    # ---------------------------
    us_any_mal_cat = False
    for r in us_results:
        if not r:
            continue
        cats = [c.lower() for c in (r.get("categories") or [])]
        if any(c in {"phishing", "malicious", "suspicious"} for c in cats):
            us_any_mal_cat = True
            break

    if us_any_mal_cat:
        score += 0.15
        reasons.append("urlscan.io: suspicious/malicious categories")
        tags.append("urlscan:malicious")

    # ---------------------------
    # Text indicators (keywords)
    # ---------------------------
        # ---------------------------
    # Text indicators (keywords)
    # ---------------------------
    if indicators:
        score += min(0.15, 0.05 * len(indicators))
        shown = ", ".join(indicators[:4]) + ("..." if len(indicators) > 4 else "")
        reasons.append(f"Indicators in text: {shown}")
        # Add both raw and prefixed tags so tests/users can check either
        # e.g., "urgent" and "indicator:urgent"
        tags.extend([kw for kw in indicators])  # raw
        tags.extend([f"indicator:{kw.lower()}" for kw in indicators])  # prefixed

    # Clamp 0..1
    score = max(0.0, min(1.0, score))

    # Traffic-light mapping
    if score >= 0.70:
        level = "Red (High)"
        tags.append("band:red")
    elif score >= 0.40:
        level = "Amber (Medium)"
        tags.append("band:amber")
    else:
        level = "Green (Low)"
        tags.append("band:green")

    # Remove duplicates, keep order
    seen = set()
    tags = [t for t in tags if not (t in seen or seen.add(t))]

    return {
        "score": round(score, 2),
        "level": level,
        "reasons": reasons,
        "tags": tags
    }
