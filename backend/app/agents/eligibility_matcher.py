"""
Agent 3: Eligibility Matcher ⭐ MOST COMPLEX

Job: Check if patient meets each trial's eligibility criteria
- Uses Chain of Thought prompting for complex nested logic
- Handles AND/OR conditions
- Identifies missing data
- Returns structured eligibility result
"""

import os
import json
from typing import Dict, Any
from datetime import datetime

import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash') if GEMINI_API_KEY else None


ELIGIBILITY_PROMPT_TEMPLATE = """
You are a clinical trial eligibility checker. Your job is to determine if a patient qualifies for a specific trial.

Follow these steps EXACTLY:

STEP 1: EXTRACT INCLUSION CRITERIA
List each inclusion criterion from the trial as a separate item.

STEP 2: CHECK PATIENT AGAINST INCLUSION
For each inclusion criterion:
- State the criterion requirement clearly
- State the patient's corresponding value
- Determine: PASS, FAIL, or MISSING (if patient data unavailable)
- Provide brief reasoning

STEP 3: EXTRACT EXCLUSION CRITERIA  
List each exclusion criterion from the trial as a separate item.

STEP 4: CHECK PATIENT AGAINST EXCLUSION
For each exclusion criterion:
- State what is excluded
- State patient's status
- Determine: MATCH (patient has this, so excluded) or NO_MATCH (patient doesn't have this, OK)
- Provide brief reasoning

STEP 5: OVERALL ELIGIBILITY
- If ANY inclusion criterion = FAIL → Status = NOT_ELIGIBLE
- If ANY exclusion criterion = MATCH → Status = NOT_ELIGIBLE  
- If ANY critical inclusion = MISSING → Status = POSSIBLY_ELIGIBLE
- If ALL inclusions = PASS and ALL exclusions = NO_MATCH → Status = ELIGIBLE

STEP 6: CONFIDENCE SCORE
- All data available, clear matches → 0.95
- Minor missing non-critical data → 0.85
- Some missing critical data → 0.70
- Significant missing data → 0.50

IMPORTANT NOTES:
- Today's date is: {current_date}
- For duration requirements (e.g., "diagnosed ≥6 months ago"), calculate from today
- Standard units: HbA1c in %, glucose in mg/dL, BP in mmHg
- If units are ambiguous, assume standard units

OUTPUT FORMAT:
You MUST output ONLY valid JSON in this exact format (no markdown, no extra text):

{{
  "status": "ELIGIBLE" | "NOT_ELIGIBLE" | "POSSIBLY_ELIGIBLE",
  "confidence": 0.95,
  "inclusion_criteria": [
    {{
      "criterion": "Age between 18 and 65 years",
      "patient_value": "52 years",
      "status": "PASS",
      "reasoning": "Patient age 52 falls within required range 18-65"
    }}
  ],
  "exclusion_criteria": [
    {{
      "criterion": "Pregnant or breastfeeding",
      "patient_value": "Male patient",
      "status": "NO_MATCH",
      "reasoning": "Patient is male, cannot be pregnant"
    }}
  ],
  "missing_data": [
    {{
      "field": "BMI",
      "reason": "Trial requires BMI 25-40, but patient BMI not provided",
      "impact": "CRITICAL"
    }}
  ]
}}

TRIAL ELIGIBILITY CRITERIA:
{trial_criteria}

PATIENT DATA:
{patient_data}

Now think step by step, then output ONLY the JSON response.
"""


async def check_eligibility(patient: Dict, trial: Dict) -> Dict[str, Any]:
    """
    Main eligibility checking function using Chain of Thought
    
    Args:
        patient: Patient profile dictionary
        trial: Trial dictionary with eligibility_criteria
    
    Returns:
        Eligibility result dictionary
    """
    
    # If no Gemini API configured, use fallback rule-based matching
    if not model:
        return fallback_eligibility_check(patient, trial)
    
    try:
        # Get trial criteria text
        trial_criteria = trial.get('eligibility_criteria', '')
        
        if not trial_criteria:
            # If no criteria, assume possibly eligible
            return {
                "status": "POSSIBLY_ELIGIBLE",
                "confidence": 0.6,
                "inclusion_criteria": [],
                "exclusion_criteria": [],
                "missing_data": [{
                    "field": "eligibility_criteria",
                    "reason": "Trial eligibility criteria not available",
                    "impact": "HIGH"
                }]
            }
        
        # Format patient data
        patient_json = json.dumps(patient, indent=2, default=str)
        
        # Generate prompt
        prompt = ELIGIBILITY_PROMPT_TEMPLATE.format(
            trial_criteria=trial_criteria,
            patient_data=patient_json,
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Call Gemini with low temperature for consistency
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048
            )
        )
        
        return parse_eligibility_response(response.text)
        
    except Exception as e:
        print(f"Error in eligibility check: {e}")
        return {
            "status": "ERROR",
            "confidence": 0.0,
            "error": str(e),
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "missing_data": []
        }


def parse_eligibility_response(response_text: str) -> Dict[str, Any]:
    """Parse Gemini response into eligibility result"""
    
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
        result = json.loads(clean_text)
        
        # Validate structure
        assert "status" in result
        assert result["status"] in ["ELIGIBLE", "NOT_ELIGIBLE", "POSSIBLY_ELIGIBLE"]
        
        # Ensure required fields
        if "confidence" not in result:
            result["confidence"] = 0.7
        if "inclusion_criteria" not in result:
            result["inclusion_criteria"] = []
        if "exclusion_criteria" not in result:
            result["exclusion_criteria"] = []
        if "missing_data" not in result:
            result["missing_data"] = []
        
        return result
        
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {response_text[:500]}")
        
        # Try to extract status from text
        status = "POSSIBLY_ELIGIBLE"
        if "NOT_ELIGIBLE" in response_text.upper() or "NOT ELIGIBLE" in response_text.upper():
            status = "NOT_ELIGIBLE"
        elif "ELIGIBLE" in response_text.upper():
            status = "ELIGIBLE"
        
        return {
            "status": status,
            "confidence": 0.5,
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "missing_data": [{
                "field": "parsing_error",
                "reason": "Could not fully parse eligibility response",
                "impact": "MEDIUM"
            }],
            "raw_response": response_text[:500]
        }


def fallback_eligibility_check(patient: Dict, trial: Dict) -> Dict[str, Any]:
    """
    Fallback rule-based eligibility check when Gemini is not available
    Uses basic criteria matching
    """
    
    inclusion_results = []
    exclusion_results = []
    missing_data = []
    
    # Check age
    patient_age = patient.get("age")
    min_age = parse_age_value(trial.get("minimum_age"))
    max_age = parse_age_value(trial.get("maximum_age"))
    
    if min_age or max_age:
        if patient_age:
            age_pass = True
            reasoning = f"Patient age {patient_age}"
            
            if min_age and patient_age < min_age:
                age_pass = False
                reasoning = f"Patient age {patient_age} is below minimum {min_age}"
            elif max_age and patient_age > max_age:
                age_pass = False
                reasoning = f"Patient age {patient_age} is above maximum {max_age}"
            else:
                reasoning = f"Patient age {patient_age} is within range"
            
            inclusion_results.append({
                "criterion": f"Age {min_age or 0}-{max_age or 'N/A'} years",
                "patient_value": str(patient_age),
                "status": "PASS" if age_pass else "FAIL",
                "reasoning": reasoning
            })
        else:
            missing_data.append({
                "field": "age",
                "reason": "Age required for eligibility",
                "impact": "CRITICAL"
            })
    
    # Check gender
    trial_gender = trial.get("gender", "ALL").upper()
    patient_gender = patient.get("gender", "").lower()
    
    if trial_gender != "ALL":
        if patient_gender:
            gender_match = (
                (trial_gender == "FEMALE" and patient_gender == "female") or
                (trial_gender == "MALE" and patient_gender == "male")
            )
            inclusion_results.append({
                "criterion": f"Gender: {trial_gender}",
                "patient_value": patient_gender,
                "status": "PASS" if gender_match else "FAIL",
                "reasoning": f"Trial requires {trial_gender.lower()} participants"
            })
        else:
            missing_data.append({
                "field": "gender",
                "reason": f"Gender required (trial is for {trial_gender.lower()} only)",
                "impact": "CRITICAL"
            })
    
    # Check conditions match
    trial_conditions = trial.get("conditions", [])
    patient_conditions = patient.get("conditions", [])
    
    if trial_conditions and patient_conditions:
        condition_match = any(
            pc.lower() in " ".join(trial_conditions).lower()
            for pc in patient_conditions
        )
        inclusion_results.append({
            "criterion": f"Condition: {', '.join(trial_conditions)}",
            "patient_value": ", ".join(patient_conditions),
            "status": "PASS" if condition_match else "FAIL",
            "reasoning": "Condition match check"
        })
    
    # Determine overall status
    failed = any(r["status"] == "FAIL" for r in inclusion_results)
    has_critical_missing = any(m["impact"] == "CRITICAL" for m in missing_data)
    
    if failed:
        status = "NOT_ELIGIBLE"
        confidence = 0.9
    elif has_critical_missing:
        status = "POSSIBLY_ELIGIBLE"
        confidence = 0.6
    elif inclusion_results:
        status = "ELIGIBLE"
        confidence = 0.8
    else:
        status = "POSSIBLY_ELIGIBLE"
        confidence = 0.5
    
    return {
        "status": status,
        "confidence": confidence,
        "inclusion_criteria": inclusion_results,
        "exclusion_criteria": exclusion_results,
        "missing_data": missing_data
    }


def parse_age_value(age_str: str) -> int:
    """Parse age from string like '18 Years' -> 18"""
    if not age_str:
        return None
    try:
        import re
        numbers = re.findall(r'\d+', str(age_str))
        return int(numbers[0]) if numbers else None
    except:
        return None
