from flask import render_template, request, jsonify
from app import app
from app.email_parser import parse_email
from app.virustotal_api import check_url
from app.urlscan_api import search_url
from app.analysis_service import fuse_signals
from app.ml_model import predict_phishing_proba  # NEW

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    raw = request.form.get('email_content', '') or ''
    parsed = parse_email(raw)
    urls = parsed.get("urls", [])

    vt_results, us_results = [], []
    for u in urls[:5]:
        vt_results.append(check_url(u))
        us_results.append(search_url(u))

    ml_prob = predict_phishing_proba(raw)  # NEW: real probability
    fusion = fuse_signals(ml_prob, vt_results, us_results, parsed.get("indicators", []))

    response = {
        "subject": parsed["subject"],
        "sender": parsed["sender"],
        "urls_checked": urls,
        "virustotal": vt_results,
        "urlscan": us_results,
        "analysis": fusion,
        "ml_probability": None if ml_prob is None else round(ml_prob, 3)
    }
    return jsonify(response)
