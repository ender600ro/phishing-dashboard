# app/urlscan_api.py
import os
import time
from typing import Dict, Optional

import requests
from app.cache import get as cache_get, set as cache_set

US_SEARCH = "https://urlscan.io/api/v1/search/"
US_SCAN   = "https://urlscan.io/api/v1/scan/"
US_RESULT = "https://urlscan.io/api/v1/result"
US_KEY    = os.getenv("URLSCAN_API_KEY", "").strip()


def search_url(url: str, timeout: int = 10) -> Optional[Dict]:
    """
    Look up recent urlscan.io results for an exact page URL (no new submission).
    Uses in-memory caching to avoid repeated requests.
    Returns a compact dict or None on network/parse error.
    """
    ck = f"us:search:{url}"
    cached = cache_get(ck)
    if cached is not None:
        return cached

    try:
        params = {"q": f'page.url:"{url}"'}
        r = requests.get(US_SEARCH, params=params, timeout=timeout)
        r.raise_for_status()
        results = r.json().get("results", []) or []
        if not results:
            result = {"seen": False}
            cache_set(ck, result)
            return result

        latest = results[0]
        verdicts = (latest.get("verdicts") or {}).get("overall") or {}
        cats = verdicts.get("categories") or []
        score = verdicts.get("score")

        result = {
            "seen": True,
            "verdict_score": score,
            "categories": cats,
            "result": latest.get("result")
        }
        cache_set(ck, result)
        return result

    except requests.RequestException:
        return None


def submit_url(url: str, public: str = "off", poll: bool = True, timeout: int = 10) -> Optional[Dict]:
    """
    Submit a new scan to urlscan.io (uses your API key). If poll=True, it will
    do a couple of quick polls for an initial verdict. Caches the final polled
    result briefly to avoid re-fetching.
    """
    if not US_KEY:
        return None

    # Check if we already cached a recent submission result for this URL
    ck = f"us:submit:{url}"
    cached = cache_get(ck)
    if cached is not None:
        return cached

    headers = {"API-Key": US_KEY, "Content-Type": "application/json"}
    try:
        # Submit
        r = requests.post(US_SCAN, json={"url": url, "public": public}, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        uuid = data.get("uuid")

        # If not polling or no uuid returned, cache the submission meta and return
        if not (poll and uuid):
            result = {"submitted": True, "uuid": uuid}
            cache_set(ck, result)
            return result

        # Quick polling loop (2–3 short tries)
        for _ in range(3):
            time.sleep(3)
            rr = requests.get(f"{US_RESULT}/{uuid}/", timeout=timeout)
            if rr.status_code == 200:
                jd = rr.json()
                verdicts = (jd.get("verdicts") or {}).get("overall") or {}
                cats = verdicts.get("categories") or []
                score = verdicts.get("score")
                result = {
                    "submitted": True,
                    "uuid": uuid,
                    "verdict_score": score,
                    "categories": cats,
                    "result_url": f"https://urlscan.io/result/{uuid}/"
                }
                cache_set(ck, result)
                return result

        # If polling didn’t return a result yet, cache the submission info
        result = {"submitted": True, "uuid": uuid}
        cache_set(ck, result)
        return result

    except requests.RequestException:
        return None
