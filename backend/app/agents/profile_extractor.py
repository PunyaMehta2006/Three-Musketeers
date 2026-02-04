"""
Agent 1: Profile Extractor

Job: Read medical documents and extract structured patient data
- Supports PDF, JPG, PNG formats
- Uses Gemini Vision for image/scanned documents
- Extracts age, gender, conditions, medications, lab values
"""

import os
import json
import re
import time
from typing import Optional
from datetime import datetime

import google.generativeai as genai
from PIL import Image
import PyPDF2
from dotenv import load_dotenv 

from app.models.patient import PatientProfile, PatientExtractionResult, Medication, LabValue


load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Gemini model
model = genai.GenerativeModel('gemini-flash-latest') if GEMINI_API_KEY else None


EXTRACTION_PROMPT = """
You are a medical document analyzer. Extract patient information from this document.

Extract the following information if present:
- Age (number)
- Gender (male/female/other)
- Location/City
- Medical conditions (list all diagnoses)
- Current medications (name, dose, frequency if available)
- Lab values:
  - HbA1c (%)
  - Fasting glucose (mg/dL)
  - Blood pressure (systolic/diastolic mmHg)
  - Cholesterol levels
  - eGFR or creatinine
  - BMI
- Allergies

OUTPUT ONLY VALID JSON (no markdown, no extra text):
{
  "age": number or null,
  "gender": "male" | "female" | "other" | null,
  "location": "city name" or null,
  "conditions": ["condition1", "condition2"] or [],
  "medications": [
    {"name": "medication name", "dose": "dose", "frequency": "frequency"}
  ] or [],
"lab_values": {
  "HbA1c": {"value": number, "unit": "%"},
  "fasting_glucose": {"value": number, "unit": "mg/dL"},
  "blood_pressure": {"value": "systolic/diastolic", "unit": "mmHg"},
  "cholesterol": {"value": number, "unit": "mg/dL"},
  "eGFR": {"value": number, "unit": "mL/min"}
} or {},
  "allergies": ["allergy1"] or []
}

If you cannot find a value, use null or empty array [].
Do NOT guess values - only extract what you can clearly see.

Document content:
"""


async def extract_patient_profile(file_path: str, file_ext: str) -> PatientExtractionResult:
    """
    Extract patient profile from upload ed document
    
    Args:
        file_path: Path to uploaded file
        file_ext: File extension (.pdf, .jpg, .png)
    
    Returns:
        PatientExtractionResult with extracted profile or error
    """
    try:
        # Extract text/image content
        if file_ext == ".pdf":
            content = extract_text_from_pdf(file_path) 
            if not content.strip():
                # PDF might be scanned - try as image
                return await extract_from_image(file_path)
            return await extract_from_text(content)
        else:
            # Image file - use Vision
            return await extract_from_image(file_path)
            
    except Exception as e:
        return PatientExtractionResult(
            success=False,
            error=str(e)
        )


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


async def extract_from_text(text: str) -> PatientExtractionResult:
    """Extract patient info from text using Gemini"""
    if not model:
        return PatientExtractionResult(
            success=False,
            error="Gemini API not configured. Please set GEMINI_API_KEY."
        )
    
    try:
        prompt = EXTRACTION_PROMPT + text[:8000]  # Limit text length
        start_time = time.time()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048
            )
        )
        
        extraction_time = time.time() - start_time
        return parse_extraction_response(response.text, extraction_time)
        
    except Exception as e:
        return PatientExtractionResult(
            success=False,
            error=f"Error calling Gemini API: {str(e)}"
        )


async def extract_from_image(file_path: str) -> PatientExtractionResult:
    """Extract patient info from image using Gemini Vision"""
    if not model:
        return PatientExtractionResult(
            success=False,
            error="Gemini API not configured. Please set GEMINI_API_KEY."
        )
    
    try:
        img = Image.open(file_path)
        start_time = time.time()
        response = model.generate_content(
            [EXTRACTION_PROMPT, img],
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048
            )
        )
        extraction_time = time.time() - start_time
        return parse_extraction_response(response.text, extraction_time)
        
    except Exception as e:
        return PatientExtractionResult(
            success=False,
            error=f"Error processing image: {str(e)}"
        )


def parse_extraction_response(response_text: str, extraction_time: float = 0.0) -> PatientExtractionResult:
    """Parse Gemini response into PatientProfile"""
    
    # Clean response - remove markdown code fences
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    try:
        data = json.loads(clean_text)
        
        # Build profile
        medications = []
        for med in data.get("medications", []):
            if isinstance(med, dict):
                medications.append(Medication(
                    name=med.get("name", "Unknown"),
                    dose=med.get("dose"),
                    frequency=med.get("frequency")
                ))
        
        lab_values = {}
        for key, value in data.get("lab_values", {}).items():
            if isinstance(value, dict) and "value" in value:
                lab_values[key] = LabValue(
                    value=value["value"],
                    unit=value.get("unit", "")
                )
        
        # Determine location tier
        location = data.get("location", "")
        location_tier = determine_location_tier(location)
        
        profile = PatientProfile(
            age=data.get("age"),
            gender=data.get("gender"),
            location=location,
            location_tier=location_tier,
            conditions=data.get("conditions", []),
            medications=medications,
            lab_values=lab_values,
            allergies=data.get("allergies", []),
            extracted_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Determine missing fields
        missing_fields = []
        if not profile.age:
            missing_fields.append("age")
        if not profile.gender:
            missing_fields.append("gender")
        if not profile.conditions:
            missing_fields.append("conditions")
        
        # Calculate confidence based on completeness
        total_fields = 7
        filled_fields = sum([
            1 if profile.age else 0,
            1 if profile.gender else 0,
            1 if profile.conditions else 0,
            1 if profile.medications else 0,
            1 if profile.lab_values else 0,
            1 if profile.location else 0,
            1 if profile.allergies else 0
        ])
        confidence = filled_fields / total_fields
        
        return PatientExtractionResult(
            success=True,
            profile=profile,
            confidence=confidence,
            missing_fields=missing_fields,
            extraction_time_seconds=round(extraction_time, 2)
        )
        
    except json.JSONDecodeError as e:
        return PatientExtractionResult(
            success=False,
            error=f"Failed to parse extraction response: {str(e)}",
            warnings=[f"Raw response: {response_text[:500]}"]
        )


def determine_location_tier(location: str) -> str:
    """Determine location tier based on city name"""
    if not location:
        return "Tier 1"
    
    location_lower = location.lower()
    
    tier_1_cities = [
        "mumbai", "delhi", "bangalore", "bengaluru", "chennai", "kolkata",
        "hyderabad", "pune", "ahmedabad"
    ]
    
    tier_2_cities = [
        "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane",
        "bhopal", "visakhapatnam", "pimpri", "patna", "vadodara",
        "ghaziabad", "ludhiana", "agra", "nashik", "faridabad", "meerut",
        "rajkot", "varanasi", "srinagar", "aurangabad", "dhanbad",
        "amritsar", "allahabad", "ranchi", "howrah", "coimbatore",
        "jabalpur", "gwalior", "vijayawada", "jodhpur", "madurai",
        "raipur", "kota", "chandigarh", "guwahati", "solapur"
    ]
    
    for city in tier_1_cities:
        if city in location_lower:
            return "Tier 1"
    
    for city in tier_2_cities:
        if city in location_lower:
            return "Tier 2"
    
    return "Tier 3"


# Fallback: Create profile from manual data
def create_profile_from_form(form_data: dict) -> PatientProfile:
    """Create patient profile from form data (fallback when extraction fails)"""
    return PatientProfile(
        age=form_data.get("age"),
        gender=form_data.get("gender"),
        location=form_data.get("location"),
        location_tier=determine_location_tier(form_data.get("location", "")),
        conditions=form_data.get("conditions", []),
        medications=[Medication(name=m) for m in form_data.get("medications", [])],
        lab_values={},
        allergies=form_data.get("allergies", [])
    )
