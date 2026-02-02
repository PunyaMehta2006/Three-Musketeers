"""
Agent 2: Trial Searcher
Searches database for trials matching patient profile
"""
from typing import List
from app.models import PatientProfile, Trial
from app.utils.database import search_trials_by_condition
async def search_trials_for_patient(
    patient: PatientProfile,
    max_results: int = 50
) -> List[Trial]:
    """
    Search for clinical trials matching patient profile
    
    Args:
        patient: PatientProfile with conditions, location, age, etc.
        max_results: Maximum number of trials to return
    
    Returns:
        List of Trial objects matching patient criteria
    """
    
    # Step 1: Search by conditions
    matching_trials = await search_trials_by_condition(
        conditions=patient.conditions,
        location=patient.location,
        limit=max_results
    )
    
    # Step 2: Filter by age and gender
    filtered_trials = []
    
    for trial_dict in matching_trials:
        # Create Trial object from dictionary
        trial = Trial(**trial_dict)
        
        # Check age eligibility
        if not is_age_eligible(patient.age, trial.minimum_age, trial.maximum_age):
            continue
        
        # Check gender eligibility
        if not is_gender_eligible(patient.gender, trial.gender):
            continue
        
        filtered_trials.append(trial)
    
    return filtered_trials
def is_age_eligible(patient_age: int, min_age: str, max_age: str) -> bool:
    """
    Check if patient age meets trial requirements
    
    Args:
        patient_age: Patient's age in years
        min_age: Trial minimum age (e.g., "18 Years", "N/A")
        max_age: Trial maximum age (e.g., "65 Years", "N/A")
    
    Returns:
        True if eligible, False otherwise
    """
    # Parse minimum age
    if min_age and min_age != "N/A":
        try:
            min_val = int(min_age.split()[0])
            if patient_age < min_val:
                return False
        except:
            pass  # If parsing fails, ignore constraint
    
    # Parse maximum age
    if max_age and max_age != "N/A":
        try:
            max_val = int(max_age.split()[0])
            if patient_age > max_val:
                return False
        except:
            pass  # If parsing fails, ignore constraint
    
    return True
def is_gender_eligible(patient_gender: str, trial_gender: str) -> bool:
    """
    Check if patient gender meets trial requirements
    
    Args:
        patient_gender: "male", "female", or "other"
        trial_gender: "MALE", "FEMALE", or "ALL"
    
    Returns:
        True if eligible, False otherwise
    """
    if not trial_gender or trial_gender == "ALL":
        return True
    
    return patient_gender.upper() == trial_gender.upper()