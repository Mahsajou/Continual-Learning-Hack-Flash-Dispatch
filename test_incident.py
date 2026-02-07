import requests
import sys
import os
import argparse

def test_upload(file_path, provider="gemini", send_email=False):
    url = "http://localhost:8000/process-recording"
    
    params = {
        "send_email": str(send_email).lower(),
        "provider": provider
    }
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return

        files = {'file': open(file_path, 'rb')}
        print(f"Uploading {file_path} to {url}...")
        print(f"Provider: {provider}, Send Email: {send_email}")
        
        response = requests.post(url, files=files, params=params)
        
        if response.status_code == 200:
            print("\n--- Success! Incident Report ---")
            print(response.json())
        else:
            print(f"\nError {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test 911 Incident Reporting Agent")
    parser.add_argument("file", help="Path to audio file")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "openai"], help="AI Provider to use")
    parser.add_argument("--email", action="store_true", help="Send email notification")
    
    args = parser.parse_args()
    
    test_upload(args.file, args.provider, args.email)
