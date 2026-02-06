# Gemini-Deepgram Native Dispatch Agent

This project implements a native voice agent using:
- **Deepgram Nova-2** for high-speed Speech-to-Text (STT).
- **Google Gemini 2.0 Flash** for incident analysis and report generation.
- **Cartesia TTS** is explicitly excluded from this workflow.

## Features
- Transcribes audio files (e.g., `call_11.mp3.mpeg`).
- Automatically extracts structured incident reports (Incident #, Type, Priority, etc.).
- Securely manages API keys via `.env`.

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the agent: `python3 main.py call_11.mp3.mpeg`
