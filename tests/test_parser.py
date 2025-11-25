from app.email_parser import parse_email

def test_parse_email_basic():
    raw = "From: Alice <a@ex.com>\nSubject: Verify your account\n\nClick https://evil.bad/login"
    out = parse_email(raw)
    assert "Alice" in out["sender"] or "a@ex.com" in out["sender"]
    assert "Verify" in out["subject"]
    assert any("http" in u for u in out["urls"])
    assert "verify" in ",".join(out["indicators"])
