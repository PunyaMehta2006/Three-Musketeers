import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("backend/.env") # Load your API Key
genai.configure(api_key='')

print("Checking available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")