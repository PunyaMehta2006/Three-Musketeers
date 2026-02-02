# Eligibility Matcher

import json
import re
import asyncio
from typing import Dict, Any
from datetime import datetime

try:
    from google import genai
except Exception:
    genai = None

client = None
MODEL_NAME = "gemini-flash-latest"

if genai:
    try:
        client = genai.Client(api_key='AIzaSyCvvkzMQd5BmjYVyM1zOKim8jNO9tlj050')
    except Exception:
        client = None

ELIGIBILITY_PROMPT_TEMPLATE = """
You are an expert clinical trial eligibility checker.

Follow these steps EXACTLY:

1. Extract inclusion criteria
2. Evaluate patient against inclusion (PASS / FAIL / MISSING)
3. Extract exclusion criteria
4. Evaluate patient against exclusion (MATCH / NO_MATCH)
5. Decide overall eligibility
6. Assign confidence score

IMPORTANT:
- Today's date: {current_date}
- Do NOT hallucinate data
- Assume standard medical units

OUTPUT ONLY valid JSON in this EXACT structure:
{{
  "status": "ELIGIBLE | NOT_ELIGIBLE | POSSIBLY_ELIGIBLE",
  "confidence": 0.0,
  "inclusion_criteria": [],
  "exclusion_criteria": [],
  "missing_data": [],
  "Final outcome": "Simple human explanation"
}}

TRIAL ELIGIBILITY CRITERIA:
{trial_criteria}

PATIENT DATA:
{patient_data}

Return ONLY JSON.
"""

async def check_eligibility(patient: Dict, trial: Dict) -> Dict[str, Any]:

    if not client:
        result = fallback_eligibility_check(patient, trial)
        result["missing_data"].insert(0, {
            "field": "llm_status",
            "reason": "LLM not configured or unavailable",
            "impact": "SYSTEM"
        })
        return result

    trial_criteria = str(trial.get("eligibility_criteria", "")).strip()

    if not trial_criteria:
        return {
            "status": "POSSIBLY_ELIGIBLE",
            "confidence": 0.6,
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "missing_data": [{
                "field": "eligibility_criteria",
                "reason": "Trial eligibility criteria missing",
                "impact": "CRITICAL"
            }],
            "Final outcome": "Trial eligibility criteria were not provided."
        }

    prompt = ELIGIBILITY_PROMPT_TEMPLATE.format(
        trial_criteria=trial_criteria,
        patient_data=json.dumps(patient, indent=2, default=str),
        current_date=datetime.now().strftime("%Y-%m-%d")
    )

    try:
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )

        return parse_eligibility_response(response.text)

    except Exception as e:
        print(f"[LLM ERROR] {e}")

        result = fallback_eligibility_check(patient, trial)
        result["missing_data"].insert(0, {
            "field": "llm_status",
            "reason": "LLM call failed, fallback logic used",
            "impact": "SYSTEM"
        })
        result["Final outcome"] = (
            "Eligibility evaluated using fallback rules because the LLM failed."
        )
        return result

def parse_eligibility_response(response_text: str) -> Dict[str, Any]:

    clean = response_text.strip()
    clean = clean.removeprefix("```json").removeprefix("```")
    clean = clean.removesuffix("```").strip()

    try:
        result = json.loads(clean)
    except Exception:
        return {
            "status": "POSSIBLY_ELIGIBLE",
            "confidence": 0.5,
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "missing_data": [{
                "field": "llm_response",
                "reason": "Invalid JSON returned by LLM",
                "impact": "MEDIUM"
            }],
            "Final outcome": "LLM response could not be parsed reliably."
        }

    result.setdefault("status", "POSSIBLY_ELIGIBLE")
    result.setdefault("confidence", 0.7)
    result.setdefault("inclusion_criteria", [])
    result.setdefault("exclusion_criteria", [])
    result.setdefault("missing_data", [])
    result.setdefault("Final outcome", "Eligibility evaluated.")

    if result["status"] not in {"ELIGIBLE", "NOT_ELIGIBLE", "POSSIBLY_ELIGIBLE"}:
        result["status"] = "POSSIBLY_ELIGIBLE"

    return result

def fallback_eligibility_check(patient: Dict, trial: Dict) -> Dict[str, Any]:

    inclusion_results = []
    exclusion_results = []
    missing_data = []

    patient_age = patient.get("age")
    min_age = parse_age_value(trial.get("minimum_age"))
    max_age = parse_age_value(trial.get("maximum_age"))

    if min_age or max_age:
        if patient_age is not None:
            if min_age and patient_age < min_age:
                inclusion_results.append({
                    "criterion": f"Minimum age {min_age}",
                    "patient_value": str(patient_age),
                    "status": "FAIL",
                    "reasoning": "Below minimum age"
                })
            elif max_age and patient_age > max_age:
                inclusion_results.append({
                    "criterion": f"Maximum age {max_age}",
                    "patient_value": str(patient_age),
                    "status": "FAIL",
                    "reasoning": "Above maximum age"
                })
            else:
                inclusion_results.append({
                    "criterion": f"Age {min_age or 0}-{max_age or 'N/A'}",
                    "patient_value": str(patient_age),
                    "status": "PASS",
                    "reasoning": "Age within allowed range"
                })
        else:
            missing_data.append({
                "field": "age",
                "reason": "Age required for eligibility",
                "impact": "CRITICAL"
            })

    trial_gender = str(trial.get("gender", "ALL")).upper()
    patient_gender = str(patient.get("gender", "")).lower()

    if trial_gender != "ALL":
        if patient_gender:
            match = (
                (trial_gender == "FEMALE" and patient_gender == "female") or
                (trial_gender == "MALE" and patient_gender == "male")
            )
            inclusion_results.append({
                "criterion": f"Gender: {trial_gender}",
                "patient_value": patient_gender,
                "status": "PASS" if match else "FAIL",
                "reasoning": "Gender eligibility check"
            })
        else:
            missing_data.append({
                "field": "gender",
                "reason": "Gender required for eligibility",
                "impact": "CRITICAL"
            })

    trial_conditions = trial.get("conditions", [])
    patient_conditions = patient.get("conditions", [])

    if trial_conditions:
        if patient_conditions:
            match = any(
                pc.lower() in " ".join(trial_conditions).lower()
                for pc in patient_conditions
            )
            inclusion_results.append({
                "criterion": f"Condition: {', '.join(trial_conditions)}",
                "patient_value": ", ".join(patient_conditions),
                "status": "PASS" if match else "FAIL",
                "reasoning": "Condition match check"
            })
        else:
            missing_data.append({
                "field": "conditions",
                "reason": "Medical conditions missing",
                "impact": "CRITICAL"
            })

    failed = any(i["status"] == "FAIL" for i in inclusion_results)
    critical_missing = any(m["impact"] == "CRITICAL" for m in missing_data)

    if failed:
        status = "NOT_ELIGIBLE"
        confidence = 0.85
    elif critical_missing:
        status = "POSSIBLY_ELIGIBLE"
        confidence = 0.6
    elif inclusion_results:
        status = "ELIGIBLE"
        confidence = 0.75
    else:
        status = "POSSIBLY_ELIGIBLE"
        confidence = 0.5

    return {
        "status": status,
        "confidence": confidence,
        "inclusion_criteria": inclusion_results,
        "exclusion_criteria": exclusion_results,
        "missing_data": missing_data,
        "Final outcome": "Eligibility determined using fallback rule-based logic."
    }

def parse_age_value(age_str: Any) -> int | None:
    if not age_str:
        return None
    try:
        match = re.search(r"\d+", str(age_str))
        return int(match.group()) if match else None
    except Exception:
        return None
    
test_patient = {
    "age": 45,
    "gender": "Male",
    "conditions": ["Type 2 Diabetes"]
}

test_trial = {
    "eligibility_criteria": "Age 18-65, Type 2 Diabetes",
    "minimum_age": "18",
    "maximum_age": "65",
    "conditions": ["Type 2 Diabetes"]
}


result = asyncio.run(check_eligibility(test_patient, test_trial))
print(json.dumps(result, indent=2))