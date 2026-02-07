# 911 Incident Reporting Agent

This project implements an AI-powered agent that processes 911 call recordings to generate structured **Incident Reports**.

It uses **Google Gemini** or **OpenAI (Whisper + GPT-4o)** to transcribe and analyze audio, extracting critical details such as dispatch information, location, involved parties, and a description of events. It can also email the generated report.

## Features

- **Audio Processing**: Upload audio recordings (MP3, WAV, M4A, etc.).
- **Multi-Provider Support**: Choose between **Google Gemini** (multimodal) or **OpenAI** (Whisper transcription + GPT-4o analysis).
- **Structured Output**: Generates a standardized JSON Incident Report.
- **Email Notifications**: Optionally sends the report via email (SMTP).

## Prerequisites

- Python 3.10+
- API Keys:
    - **Google Gemini API Key** (for Gemini mode)
    - **OpenAI API Key** (for OpenAI mode)
- SMTP Server details (if using email notifications)

## Setup

1.  **Clone the repository:**

2.  **Configure Environment:**
    Create a `.env` file based on `env.example`.
    ```bash
    cp env.example .env
    # On Windows PowerShell:
    # Copy-Item env.example .env
    ```
    Edit `.env` and add your keys:
    ```ini
    # AI Providers
    GEMINI_API_KEY=your_gemini_key
    OPENAI_API_KEY=your_openai_key

    # Email (Optional)
    SMTP_SERVER=smtp.gmail.com
    # ... other email settings
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Start the Server
```bash
python server.py
```
The server will start on port 8000.

### 2. Test the Agent
Use the included `test_incident.py` script to upload an audio file and see the result.

**Standard Test (Uses Default Provider - Gemini):**
```bash
python test_incident.py path/to/your/audio.mp3
```

**Test with OpenAI:**
```bash
python test_incident.py path/to/your/audio.mp3 --provider openai
```

**Test with Email Notification:**
```bash
python test_incident.py path/to/your/audio.mp3 --email
```

### 3. API Endpoint
**POST** `http://localhost:8000/process-recording`

**Parameters:**
- `file`: Audio file (multipart/form-data)
- `provider`: `gemini` (default) or `openai` (query param)
- `send_email`: `true` or `false` (default `false`) (query param)

