import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    FileSource,
)
from google import genai

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VoiceAgent:
    def __init__(self):
        self.api_key_deepgram = os.getenv("DEEPGRAM_API_KEY")
        self.api_key_gemini = os.getenv("GEMINI_API_KEY")

        if not self.api_key_deepgram:
            logging.error("DEEPGRAM_API_KEY not set")
        if not self.api_key_gemini:
            logging.error("GEMINI_API_KEY not set")

        # Initialize Deepgram
        self.dg_client = DeepgramClient(self.api_key_deepgram)
        
        # Initialize Gemini
        self.gemini_client = genai.Client(api_key=self.api_key_gemini)
        self.gemini_model = "gemini-2.0-flash" 
        self.chat_session = self.gemini_client.chats.create(model=self.gemini_model)

    async def process_file(self, file_path):
        """Transcribe a file and pass it to Gemini."""
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return

        logging.info(f"Processing audio file: {file_path}")
        
        try:
            with open(file_path, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            options = {
                "model": "nova-2",
                "smart_format": True,
            }

            response = self.dg_client.listen.rest.v("1").transcribe_file(payload, options)
            transcript = response.results.channels[0].alternatives[0].transcript
            
            logging.info(f"User (from file): {transcript}")
            
            if transcript:
                llm_response = self.chat_session.send_message(transcript)
                logging.info(f"Gemini: {llm_response.text}")
                logging.info("--> [TTS Skipped] Workflow for Cartesia is omitted.")
            
        except Exception as e:
            logging.error(f"Error processing file: {e}")

    async def start_live(self):
        """Placeholder for live microphone stream handling."""
        print("Starting Live Gemini-Deepgram Native Agent (TTS Disabled)...")
        # Live implementation would go here...
        while True:
            await asyncio.sleep(1)

async def main():
    agent = VoiceAgent()
    
    # Check if call_11.mp3 exists to process it as requested
    test_file = "call_11.mp3"
    if os.path.exists(test_file):
        await agent.process_file(test_file)
    else:
        logging.info(f"{test_file} not found. Starting in live/wait mode.")
        await agent.start_live()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)