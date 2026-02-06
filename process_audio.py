import os
import asyncio
from dotenv import load_dotenv
from deepgram import DeepgramClient
from google import genai

load_dotenv()

async def process_call(file_path):
    # 1. Setup Clients
    dg_api_key = os.getenv("DEEPGRAM_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not dg_api_key or not gemini_api_key:
        print("Error: Missing API keys in .env")
        return

    # 2. Transcribe with Deepgram
    print(f"Transcribing {file_path}...")
    try:
        deepgram = DeepgramClient(dg_api_key)
        
        with open(file_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {"buffer": buffer_data}
        options = {"model": "nova-2", "smart_format": True}

        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        transcript = response.results.channels[0].alternatives[0].transcript
        
        print("\n--- Raw Transcript ---")
        print(transcript)
        print("----------------------\n")

    except Exception as e:
        print(f"Transcription Error: {e}")
        return

    # 3. Analyze with Gemini
    print("Generating Incident Report with Gemini...")
    try:
        client = genai.Client(api_key=gemini_api_key)
        
        prompt = f"""
        You are an expert emergency dispatcher and incident reporter. 
        Analyze the following transcript of an emergency call and strictly extract the details to fill out the report below. 
        
        If a specific detail is not mentioned in the audio, write "Not mentioned" or "Unknown".
        Do not halluncinate information.

        --- REPORT FORMAT ---
        1. Initial Call (Dispatch) Information 
        * Incident Number/Case Number: 
        * Date and Time of Call/Dispatch: 
        * Address/Location of Occurrence: 
        * Incident Type/Nature of Call: 
        * Priority Level: 

        2. General Incident Details
        * Names and Contact Info: 
        * Description of Events: 
        * Scene Description: 
        * Evidence/Property: 

        --- TRANSCRIPT ---
        {transcript}
        """

        response = client.chats.create(model="gemini-2.0-flash").send_message(prompt)
        
        print("\n=== GENERATED INCIDENT REPORT ===")
        print(response.text)
        print("=================================")

    except Exception as e:
        print(f"Gemini Analysis Error: {e}")

if __name__ == "__main__":
    file_name = "call_11.mp3.mpeg"
    if os.path.exists(file_name):
        asyncio.run(process_call(file_name))
    else:
        print(f"File {file_name} not found.")
