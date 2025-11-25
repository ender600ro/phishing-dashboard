from app.analysis_service import fuse_signals

def test_fusion_rules():
    # ML says neutral; VT says 1 malicious; urlscan flags phishing
    vt = [{"seen": True, "malicious": 1, "suspicious": 0, "harmless": 0}]
    us = [{"seen": True, "categories": ["phishing"], "verdict_score": 100}]
    out = fuse_signals(0.3, vt, us, ["urgent"])
    assert out["score"] >= 0.7
    assert out["level"].startswith("Red")
    assert "urgent" in out["tags"]