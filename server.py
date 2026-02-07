"""FastAPI server for 911 Incident Reporting."""

from __future__ import annotations

import os
import shutil
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Query
from loguru import logger
import uvicorn

from processor import RecordingProcessor
import email_service

load_dotenv()

# Configuration
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

app = FastAPI(
    title="911 Incident Reporting Agent",
    description="Process 911 call recordings and generate incident reports using Gemini.",
    version="1.0.0",
)

@app.get("/")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "911-incident-reporting",
    }

@app.post("/process-recording")
async def process_recording_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    send_email: bool = Query(default=False),
    provider: str = Query(default="gemini", description="AI Provider: 'gemini' or 'openai'"),
) -> dict:
    """
    Process an uploaded audio recording and generate an incident report.
    """
    logger.info(f"Received recording: {file.filename}, provider={provider}, send_email={send_email}")
    
    # Check if file is provided
    if not file.filename:
         return {"error": "No file uploaded"}

    # Save uploaded file to temp
    suffix = f".{file.filename.split('.')[-1]}" if "." in file.filename else ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        processor = RecordingProcessor()
        # Determine mime type based on extension or default to audio/mp3
        mime_type = file.content_type or "audio/mp3"
        
        report = processor.process_recording(tmp_path, mime_type=mime_type, provider=provider)
        
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        if send_email:
            background_tasks.add_task(email_service.send_incident_report_email, report)
            
        return report.model_dump()

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return {"error": str(e)}

def main() -> None:
    """Run the server."""
    logger.info(f"Starting 911 Incident Reporting Agent on port {SERVER_PORT}")
    uvicorn.run("server:app", host="0.0.0.0", port=SERVER_PORT, log_level="info")

if __name__ == "__main__":
    main()
