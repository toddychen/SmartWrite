#!/usr/bin/env python3

import datetime
import sys
import json
import os
from google import genai
from google.genai import types

CREDENTIALS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "credentials", "gemini.json"
)

"""
Usage:
    python3 rephrase_gemini.py <text_to_rephrase> [tone] [enable_log]

Example:
    python3 rephrase_gemini.py "Hello world" professional log
"""

try:
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        creds = json.load(f)
        API_KEY = creds.get("api_key")
        if not API_KEY:
            raise ValueError("No 'api_key' found in gemini.json")
except FileNotFoundError:
    print(f"Error: Credentials file not found at {CREDENTIALS_PATH}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in {CREDENTIALS_PATH}")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: rephrase_gemini.py <text_to_rephrase> [tone] [enable_log]")
    print("Example tones: formal, casual, friendly, professional, humorous, etc.")
    sys.exit(1)

text = sys.argv[1].strip()
tone = sys.argv[2].strip() if len(sys.argv) >= 3 else "neutral"
enable_log = sys.argv[3].strip().lower() in {'yes', 'log'} if len(sys.argv) >= 4 else True
system_instruction = f"You are a helpful assistant who rephrases text in a {tone} tone."

client = genai.Client(api_key=API_KEY)
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=f"Please rephrase the following text. ONLY reply with the rephrased text, no explanations or extra commentary: \n{text}",
    )
except Exception as e:
    print(f"Error calling Gemini API: {e}")
    sys.exit(1)

def log_io(input_text, output_text, log=True):
    if not log:
        return
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    parent_dir = os.path.dirname(current_dir)
    log_dir = os.path.join(parent_dir, 'log')
    os.makedirs(log_dir, exist_ok=True)
    logfile_path = os.path.join(log_dir, "log.txt")

    with open(logfile_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} - INPUT:\n{input_text}\n")
        f.write(f"{datetime.datetime.now().isoformat()} - OUTPUT:\n{output_text}\n")
        f.write("-" * 40 + "\n")

log_io(text, response.text, enable_log)

print(response.text)
