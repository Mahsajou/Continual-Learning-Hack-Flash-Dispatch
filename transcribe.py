import os
import sys
import asyncio
import json
from dotenv import load_dotenv
from deepgram import DeepgramClient, FileSource

load_dotenv()

async def transcribe_audio(file_path):
    dg_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not dg_api_key:
        print("Error: DEEPGRAM_API_KEY is not set in .env")
        return

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        deepgram = DeepgramClient(dg_api_key)

        with open(file_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = {
            "model": "nova-2",
            "smart_format": True,
        }

        print(f"Transcribing {file_path}...")
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        
        transcript = response.results.channels[0].alternatives[0].transcript
        print("\n--- Transcript ---")
        print(transcript)
        print("------------------\n")
        
        return transcript

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    file_to_process = "call_11.mp3"
    if len(sys.argv) > 1:
        file_to_process = sys.argv[1]
    
    asyncio.run(transcribe_audio(file_to_process))