import google.generativeai as genai
import json
import os
import time
import random
from PIL import Image
import io
from dotenv import load_dotenv
# 1. SETUP
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY not found in .env file. Please add it.")
genai.configure(api_key=GOOGLE_API_KEY)
# 2. USE THE LITE MODEL (Higher free tier limits)
model = genai.GenerativeModel('models/gemini-flash-latest')
def extract_profile_from_image(image_bytes, max_retries=3):
    """
    Agent 1 Logic: Precise extraction using the Gemini Flash Lite model.
    Includes retry logic with exponential backoff for rate limiting.
    """
    
    # Load image
    image = Image.open(io.BytesIO(image_bytes))
    prompt = """
    You are a medical data extraction assistant. 
    Analyze this document and extract patient details into this EXACT JSON structure.
    
    Fields to extract:
    - conditions (list of strings, e.g. ["Type 2 Diabetes"])
    - age (integer or null)
    - gender (string or null)
    - location (string or null)
    - medications (list of strings)
    - lab_values (dictionary)
    Rules:
    1. Only output valid JSON. No markdown formatting.
    2. If a field is not found, use null.
    """
    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            # API Call
            response = model.generate_content([prompt, image])
            
            # Check if response has valid content
            if not response.candidates or not response.text:
                raise ValueError("Empty response from API")
            
            # Parse Response
            text_response = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text_response)
        except Exception as e:
            error_str = str(e)
            
            # Handle rate limiting (429 error)
            if "429" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    print(f"⏳ Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Agent 1 Error: Rate limit exceeded after {max_retries} retries")
                    return {
                        "error": "Rate limit exceeded. Please try again in a minute.",
                        "conditions": [],
                        "age": None
                    }
            else:
                # Other errors - log and return fallback
                print(f"❌ Agent 1 Error: {e}")
                return {
                    "error": str(e),
                    "conditions": [],
                    "age": None
                }
    
    # Fallback if all retries exhausted
    return {
         "error": "Failed after all retries",
        "conditions": [],
        "age": None
    }