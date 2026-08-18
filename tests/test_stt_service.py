"""Basic tests for the STT service's /transcribe endpoint."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from services.stt.main import app

client = TestClient(app)


def test_rejects_wrong_file_type():
    """Uploading a non-audio file should return 400, not crash."""
    response = client.post(
        "/transcribe",
        files={"file": ("test.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 400


def test_rejects_empty_file():
    """An empty audio file should be rejected with a clean 400."""
    response = client.post(
        "/transcribe",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400


def test_accepts_valid_audio():
    """A real WAV file should return 200 with a transcript."""
    with open("scripts/output_en-IN.wav", "rb") as f:
        response = client.post(
            "/transcribe",
            files={"file": ("output_en-IN.wav", f, "audio/wav")},
        )
    assert response.status_code == 200
    assert "text" in response.json()