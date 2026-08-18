"""Basic tests for the TTS service's /synthesize endpoint."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from services.tts.main import app

client = TestClient(app)


def test_rejects_invalid_language():
    """An unsupported language code should return 400, not crash."""
    response = client.post("/synthesize", json={"text": "hello", "language": "xx"})
    assert response.status_code == 400


def test_rejects_empty_text():
    """Empty text should be rejected with a clean 400."""
    response = client.post("/synthesize", json={"text": "   ", "language": "en"})
    assert response.status_code == 400


def test_accepts_valid_request():
    """A valid text + language should return 200 with WAV audio."""
    response = client.post(
        "/synthesize", json={"text": "Hello, welcome to the hospital", "language": "en"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"