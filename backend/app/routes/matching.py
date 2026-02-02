"""
Matching routes - Match patients to trials
"""
from fastapi import APIRouter
from app.models import PatientProfile
from app.agents import search_trials_for_patient
router = APIRouter(prefix="/api", tags=["matching"])
@router.post("/match-trials")
async def match_patient_to_trials(patient: PatientProfile):
    """
    Find trials matching patient profile
    Uses Agent 2 to search and filter trials
    
    Args:
        patient: PatientProfile with conditions, age, gender, etc.
    
    Returns:
        List of matching trials
    """
    # Use Agent 2 to search for matching trials
    matching_trials = await search_trials_for_patient(
        patient=patient,
        max_results=50
    )
    
    return {
        "patient_age": patient.age,
        "patient_gender": patient.gender,
        "patient_conditions": patient.conditions,
        "total_matches": len(matching_trials),
        "trials": [trial.dict() for trial in matching_trials]
    }