import asyncio
from app.models import PatientProfile
from app.agents import search_trials_for_patient
async def test_trial_search():
    # Create a test patient
    patient = PatientProfile(
        age=52,
        gender="male",
        location="Mumbai",
        location_tier="Tier 1",
        conditions=["Type 2 Diabetes", "Hypertension"]
    )
    
    print(f"  Searching for trials matching:")
    print(f"   Age: {patient.age}")
    print(f"   Gender: {patient.gender}")
    print(f"   Conditions: {patient.conditions}")
    print(f"   Location: {patient.location}")
    
    # Search for trials
    trials = await search_trials_for_patient(patient, max_results=10)
    
    print(f"\n Found {len(trials)} matching trials:")
    
    for i, trial in enumerate(trials[:5], 1):  # Show first 5
        print(f"\n{i}. {trial.title}")
        print(f"   NCT ID: {trial.nct_id}")
        print(f"   Status: {trial.status}")
        print(f"   Phase: {trial.phase}")
        print(f"   Conditions: {', '.join(trial.conditions[:3])}")
        print(f"   Age: {trial.minimum_age} - {trial.maximum_age}")
        print(f"   Gender: {trial.gender}")
# Run test
if __name__ == "__main__":
    asyncio.run(test_trial_search())