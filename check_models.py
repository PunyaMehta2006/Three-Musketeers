import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("backend/.env") # Load your API Key
<<<<<<< HEAD
genai.configure(api_key='')
=======
genai.configure(api_key='AIzaSyAer_to0zU95ZIZeg4a1ghuWszueokv7uk')

>>>>>>> 3c6c5fe1045b101645f4b940775ef9298ca60139
print("Checking available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")