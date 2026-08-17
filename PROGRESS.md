## Team A — Week 1
- Set up project structure (services/, tests/, scripts/), venv, requirements.txt
- Sarvam API key configured with fail-loud loader
- TTS smoke test: Kannada, Hindi, English audio all produced and verified (bulbul:v2)
- STT smoke test: correct transcripts for Kannada/Hindi; minor mishearing on English
  ("Hello" → "Fellow") — flagged as expected STT variance, not a pipeline bug
- Model names corrected from roadmap doc: saarika:v2.5 (not saaras:v2/saarika:v2,
  both deprecated); multipart uploads need explicit (filename, file, content-type) tuple
- Manual voice-echo demo working end to end
- Git/GitHub setup deferred — will commit full week's work in one batch
- Blockers: none