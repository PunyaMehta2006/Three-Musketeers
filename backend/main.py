import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
TRIALS_DATA = []
try:
    print("loading trials_10k.json...")
    with open("trials_10k.json", "r") as f:
        TRIALS_DATA = json.load(f)
    print(f"Loaded {len(TRIALS_DATA)} trials.")
except FileNotFoundError:
    print("ERROR: file not found.")
@app.get("/")
def home():
    return {"message": "Hello, World!","trials_count": len(TRIALS_DATA)}