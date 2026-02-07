import os
import json
from google import genai
from google.genai import types
from loguru import logger
from dotenv import load_dotenv
import openai

from incident_model import IncidentReport

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

class RecordingProcessor:
    def __init__(self):
        # Gemini Init
        if GEMINI_API_KEY:
             self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        else:
             logger.warning("GEMINI_API_KEY not found.")
             self.gemini_client = None

        # OpenAI Init
        if OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            logger.warning("OPENAI_API_KEY not found.")
            self.openai_client = None

    def process_recording(self, file_path: str, mime_type: str = "audio/mp3", provider: str = "gemini") -> IncidentReport:
        """
        Processes recording using the specified provider.
        """
        logger.info(f"Processing with provider: {provider}")
        
        if provider.lower() == "openai":
            return self._process_with_openai(file_path)
        else:
            return self._process_with_gemini(file_path, mime_type)

    def _process_with_gemini(self, file_path: str, mime_type: str) -> IncidentReport:
        if not self.gemini_client:
            raise ValueError("Gemini client not initialized. Check GEMINI_API_KEY.")

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            prompt = self._get_system_prompt()

            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type,
                                    data=file_content
                                )
                            )
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=IncidentReport
                )
            )
            
            if response.parsed:
                return response.parsed
            else:
                return IncidentReport.model_validate_json(response.text)

        except Exception as e:
            logger.error(f"Gemini processing error: {e}")
            raise e

    def _process_with_openai(self, file_path: str) -> IncidentReport:
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        try:
            # Step 1: Transcribe with Whisper
            logger.info("Transcribing audio with Whisper...")
            with open(file_path, "rb") as audio_file:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            
            transcript_text = transcription.text
            logger.info(f"Transcript generated ({len(transcript_text)} chars). Extracting data...")

            # Step 2: Extract content with GPT-4o
            completion = self.openai_client.beta.chat.completions.parse(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"Here is the transcript of the 911 call:\n\n{transcript_text}"}
                ],
                response_format=IncidentReport,
            )

            report = completion.choices[0].message.parsed
            return report

        except Exception as e:
            logger.error(f"OpenAI processing error: {e}")
            raise e

    def _get_system_prompt(self) -> str:
        return """
        You are a 911 dispatch AI. Analyze the input (audio or transcript) and generate a structured Incident Report.
        Extract all relevant details into the specified JSON format.
        
        If information is missing, leave it as null or "Unknown".
        
        Focus on:
        1. Accurate timestamps if mentioned.
        2. Verified addresses.
        3. Clear description of the emergency.
        4. Identifying all people involved and their roles.
        """
