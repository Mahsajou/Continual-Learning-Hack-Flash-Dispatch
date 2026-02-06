import os
import asyncio
import sys
import logging
from dotenv import load_dotenv

from deepgram import DeepgramClient
from google import genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FlashDispatchAgent:
    def __init__(self):
        self.dg_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.dg_api_key or not self.gemini_api_key:
            logging.error("Missing DEEPGRAM_API_KEY or GEMINI_API_KEY in .env file.")
            sys.exit(1)

        # Initialize Clients
        self.dg_client = DeepgramClient(api_key=self.dg_api_key)
        self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        self.model_id = "gemini-2.0-flash"

    async def transcribe(self, file_path):
        """Transcribes audio using Deepgram Nova-2."""
        logging.info(f"Transcribing audio: {file_path}")
        try:
            with open(file_path, "rb") as file:
                buffer_data = file.read()

            options = {"model": "nova-2", "smart_format": True}
            response = self.dg_client.listen.v1.media.transcribe_file(request=buffer_data, **options)
            transcript = response.results.channels[0].alternatives[0].transcript
            return transcript
        except Exception as e:
            logging.error(f"Transcription Error: {e}")
            return None

    async def generate_report(self, transcript):
        """Generates a structured incident report using Gemini."""
        logging.info("Analyzing transcript and generating report...")
        prompt = f"""
        You are an expert emergency dispatcher. Analyze the transcript below and extract details into the following fields.
        If a detail is missing, write "Not mentioned".

        --- REPORT FIELDS ---
        1. Initial Call (Dispatch) Information 
        - Incident Number/Case Number:
        - Date and Time of Call/Dispatch:
        - Address/Location of Occurrence:
        - Incident Type/Nature of Call:
        - Priority Level: 

        2. General Incident Details
        - Names and Contact Info:
        - Description of Events:
        - Scene Description:
        - Evidence/Property:

        --- TRANSCRIPT ---
        {transcript}
        """
        try:
            response = self.gemini_client.chats.create(model=self.model_id).send_message(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Gemini Error: {e}")
            return None

    async def run(self, file_path):
        """End-to-end execution."""
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return

        transcript = await self.transcribe(file_path)
        if transcript:
            print("\n--- RAW TRANSCRIPT ---")
            print(transcript)
            print("-" * 25)
            
            report = await self.generate_report(transcript)
            if report:
                print("\n=== GENERATED INCIDENT REPORT ===")
                print(report)
                print("=" * 35)
                
                # Save report to file
                report_file = f"{os.path.splitext(file_path)[0]}_report.txt"
                with open(report_file, "w") as f:
                    f.write(report)
                print(f"\nReport saved to: {report_file}")

async def main():
    agent = FlashDispatchAgent()
    
    # Use command line argument if provided, else default to call_11.mp3.mpeg
    file_to_process = sys.argv[1] if len(sys.argv) > 1 else "call_11.mp3.mpeg"
    await agent.run(file_to_process)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
