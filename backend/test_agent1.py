"""
Test Agent 1 - Profile Extractor
"""
import asyncio
from app.models import ManualPatientInput
# Test with manual form data (simpler than PDF for now)
async def test_manual_input():
    # Create sample patient data
    form_data = ManualPatientInput(
        age=52,
        gender="male",
        location="Mumbai",
        primary_condition="Type 2 Diabetes",
        hba1c=8.7,
        other_conditions="Hypertension"
    )
    
    # Convert to PatientProfile
    profile = form_data.to_patient_profile()
    
    print("✅ Manual input test passed!")
    print(f"   Patient: {profile.age}y {profile.gender}")
    print(f"   Location: {profile.location} (Tier {profile.location_tier})")
    print(f"   Conditions: {profile.conditions}")
    print(f"   HbA1c: {profile.lab_values.get('HbA1c').value if profile.lab_values.get('HbA1c') else 'N/A'}%")
# Run test
if __name__ == "__main__":
    asyncio.run(test_manual_input())