"""
STT microservice.
Wraps Sarvam Saarika v2.5 behind a FastAPI endpoint so other services
(the future Channel Gateway, etc.) can call transcription over HTTP
instead of hitting Sarvam directly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from services.config import SARVAM_API_KEY, SARVAM_BASE_URL

assert SARVAM_API_KEY is not None

app = FastAPI(title="Zenvy STT Service")

ALLOWED_CONTENT_TYPES = {"audio/wav", "audio/x-wav", "audio/wave", "audio/mpeg", "audio/mp3"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Accept an uploaded audio file, forward it to Sarvam Saarika v2.5,
    and return the transcript and detected language.
    Validates file type and size before calling the API, and returns
    a clean error instead of crashing on bad input or upstream failures.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )

    audio_bytes = await file.read()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(audio_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit.")

    print(f"[STT] Received file: {file.filename}, {len(audio_bytes)} bytes")

    try:
        response = requests.post(
            f"{SARVAM_BASE_URL}/speech-to-text",
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": (file.filename, audio_bytes, "audio/wav")},
            data={"model": "saarika:v2.5"},
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[STT] Sarvam API error: {e}")
        raise HTTPException(status_code=502, detail="STT provider request failed.")

    result = response.json()
    print(f"[STT] Transcript: {result.get('transcript')} | Lang: {result.get('language_code')}")

    return {
        "text": result.get("transcript"),
        "language_code": result.get("language_code"),
    }