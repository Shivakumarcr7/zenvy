import os
import base64
import requests

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Zenvy Voice Lab")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("SARVAM_API_KEY")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/api/stt")
async def speech_to_text(
    file: UploadFile = File(...),
    language_code: str = Form("unknown")
):
    if not API_KEY:
        return {"error": "SARVAM_API_KEY not configured"}

    audio = await file.read()

    files = {
        "file": (
            file.filename,
            audio,
            file.content_type or "audio/wav"
        )
    }

    data = {
        "model": "saaras:v3",
        "language_code": language_code
    }

    headers = {
        "api-subscription-key": API_KEY
    }

    response = requests.post(
        "https://api.sarvam.ai/speech-to-text",
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code != 200:
        return {
            "error": "STT failed",
            "details": response.text
        }

    return response.json()


@app.post("/api/tts")
async def text_to_speech(
    text: str = Form(...),
    language_code: str = Form("kn-IN"),
    speaker: str = Form("shubh")
):
    if not API_KEY:
        return {"error": "SARVAM_API_KEY not configured"}

    data = {
        "text": text,
        "target_language_code": language_code,
        "speaker": speaker,
        "model": "bulbul:v3"
    }

    headers = {
        "api-subscription-key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        return {
            "error": "TTS failed",
            "details": response.text
        }

    result = response.json()

    return {
        "audio": result["audios"][0]
    }