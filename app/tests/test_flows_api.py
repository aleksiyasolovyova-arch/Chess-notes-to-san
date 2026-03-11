from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_validate_english_moves():
    """Validate English moves through the HTTP endpoint."""
    payload = {"moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "h6", "Bh4", "O-O"], "ui_lang": "en"}

    resp = client.post("/api/validate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "legal" in data
    assert data["legal"] is True
    assert len(data["moves"]) == len(payload["moves"])


def test_api_validate_french_moves():
    """Validate French moves and ensure original notation is returned."""
    payload = {"moves": ["e4", "e5", "Cf3", "Cc6"], "ui_lang": "fr"}

    resp = client.post("/api/validate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    returned_moves = [m["move"] for m in data["moves"]]
    assert returned_moves == payload["moves"]


def test_api_validate_rejects_invalid_lang():
    """Unsupported language code should result in 400 error."""
    payload = {"moves": ["e4"], "ui_lang": "de"}

    resp = client.post("/api/validate", json=payload)
    assert resp.status_code == 400
