import json
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# Import the function you just tested
from profile_extractor import extract_profile_from_image

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOAD DATA (Your existing code) ---
TRIALS_DATA = []
try:
    # Use relative path to be safe
    # If main.py is in backend/, and data is in ../data/
    file_path = os.path.join(os.path.dirname(__file__), "../data/trials_10k.json")
    
    print(f"Loading trials from: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        TRIALS_DATA = json.load(f)
    print(f" Loaded {len(TRIALS_DATA)} trials.")
except FileNotFoundError:
    print(" ERROR: trials_10k.json not found. Did you run download_trials.py?")

@app.get("/")
def home():
    return {
        "message": "DiversityMatch.AI Backend Running",
        "trials_loaded": len(TRIALS_DATA)
    }

# --- NEW: AGENT 1 ENDPOINT ---
@app.post("/api/extract-profile")
async def extract_profile_endpoint(file: UploadFile = File(...)):
    """
    Receives a PDF/Image, sends it to Gemini (Agent 1), returns JSON profile.
    """
    try:
        # 1. Read the file
        content = await file.read()
        
        # 2. Process with your profile_extractor.py
        result = extract_profile_from_image(content)
        
        # 3. Return the result
        return result
        
    except Exception as e:
        return {"error": f"Server Error: {str(e)}"}