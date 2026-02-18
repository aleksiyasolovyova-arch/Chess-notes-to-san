import io
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_scoresheets_upload_mock_image():
    """Upload a fake image and check we get parsed moves back."""
    file_content = b"fake image data"
    files = {"file": ("scoresheet.jpg", io.BytesIO(file_content), "image/jpeg")}

    resp = client.post("/api/scoresheets", files=files)
    assert resp.status_code == 200

    data = resp.json()
    # Basic fields from mock OCR
    assert data["filename"] == "scoresheet.jpg"
    assert "white" in data and "black" in data
    assert "moves" in data
    assert isinstance(data["moves"], list)
    assert len(data["moves"]) > 0

    first = data["moves"][0]
    # Check DTO shape
    assert "raw_input" in first
    assert "san_intent" in first
    assert "piece" in first
    assert "destination" in first



def test_api_validate_english_moves():
    """Validate English moves through the HTTP endpoint."""
    payload = {"moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "h6", "Bh4", "O-O"], "lang": "en"}

    resp = client.post("/api/validate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "all_legal" in data
    assert data["all_legal"] is True
    assert len(data["moves"]) == len(payload["moves"])


def test_api_validate_french_moves():
    """Validate French moves and ensure original notation is returned."""
    payload = {"moves": ["e4", "e5", "Cf3", "Cc6"], "lang": "fr"}

    resp = client.post("/api/validate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    # Moves in response should be exactly what we sent in
    returned_moves = [m["move"] for m in data["moves"]]
    assert returned_moves == payload["moves"]


def test_api_validate_rejects_invalid_lang():
    """Unsupported language code should result in 400 error."""
    payload = {"moves": ["e4"], "lang": "de"}

    resp = client.post("/api/validate", json=payload)
    assert resp.status_code == 400
