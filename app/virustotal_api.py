# app/virustotal_api.py
import os
import base64
import requests
from typing import Dict, Optional
from app.cache import get as cache_get, set as cache_set


VT_BASE = "https://www.virustotal.com/api/v3"
VT_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

def _url_id(url: str) -> str:
    """
    VT's /urls/{id} uses urlsafe base64 of the raw URL without padding.
    """
    b = base64.urlsafe_b64encode(url.encode("utf-8")).decode("utf-8")
    return b.strip("=")

def check_url(url: str, timeout: int = 10) -> Optional[Dict]:
    """
    Queries VT without submitting a fresh scan (quota-friendly):
    GET /api/v3/urls/{id}
    Returns a compact verdict dict or None on error.
    """
    if not VT_KEY:
        return None
    urlid = _url_id(url)
    headers = {"x-apikey": VT_KEY}
    try:
        r = requests.get(f"{VT_BASE}/urls/{urlid}", headers=headers, timeout=timeout)
        if r.status_code == 404:
            # Not seen by VT; you *could* POST /urls to submit, but that burns quota.
            return {"seen": False, "malicious": 0, "suspicious": 0, "harmless": 0}
        r.raise_for_status()
        data = r.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {}) or {}
        cat = data.get("categories", {}) or {}
        malicious = int(stats.get("malicious", 0))
        suspicious = int(stats.get("suspicious", 0))
        harmless = int(stats.get("harmless", 0))
        return {
            "seen": True,
            "malicious": malicious,
            "suspicious": suspicious,
            "harmless": harmless,
            "categories": cat
        }
    except requests.RequestException:
        return None
