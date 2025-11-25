# app/email_parser.py
import re
from typing import Dict, List

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "password", "account", "login", "update",
    "confirm", "suspend", "invoice", "payment", "bank", "credential",
    "limited time", "click here", "reset", "security alert"
]

URL_REGEX = re.compile(
    r'((?:https?://|ftp://|www\.)[^\s<>")\'\]]+)',
    flags=re.IGNORECASE
)

def extract_urls(text: str) -> List[str]:
    if not text:
        return []
    urls = URL_REGEX.findall(text)
    # Normalise: add http scheme if user pasted “www.”
    normalised = []
    for u in urls:
        if u.lower().startswith("www."):
            normalised.append("http://" + u)
        else:
            normalised.append(u)
    # Deduplicate while preserving order
    seen = set()
    out = []
    for u in normalised:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out

def extract_header_field(raw: str, field: str) -> str:
    """
    Very simple header grabber; good enough for demos.
    Looks for lines like 'Subject: ...' or 'From: ...'
    """
    if not raw:
        return ""
    pattern = re.compile(rf'^{field}:\s*(.+)$', re.IGNORECASE | re.MULTILINE)
    m = pattern.search(raw)
    return m.group(1).strip() if m else ""

def find_indicators(text: str) -> List[str]:
    if not text:
        return []
    lower = text.lower()
    hits = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lower]
    # Heuristic examples
    if re.search(r'(?i)unicode|punycode|xn--', text):
        hits.append("unicode/punycode")
    if re.search(r'(?i)\bverify\b.*\baccount\b', text):
        hits.append("verify-account-phrase")
    return sorted(set(hits))

def parse_email(raw_text: str) -> Dict:
    urls = extract_urls(raw_text)
    subject = extract_header_field(raw_text, "Subject")
    sender = extract_header_field(raw_text, "From")
    flags = find_indicators(raw_text)
    return {
        "subject": subject,
        "sender": sender,
        "urls": urls,
        "indicators": flags,
        "length": len(raw_text or "")
    }
