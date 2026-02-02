
#Patient data model


from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class Medication(BaseModel):
    #Patient medication details
    name: str 
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration_months: Optional[int] = None


class LabValue(BaseModel):
    #Lab test result
    value: float
    unit: str
    date: Optional[str] = None


class PatientProfile(BaseModel):
    #Complete patient profile extracted from documents or manual input
    patient_id: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    location: Optional[str] = None
    location_tier: Optional[str] = Field(None, pattern="^(Tier 1|Tier 2|Tier 3)$")
    conditions: List[str] = Field(default_factory=list)
    medications: List[Medication] = Field(default_factory=list)
    lab_values: Dict[str, LabValue] = Field(default_factory=dict)
    allergies: List[str] = Field(default_factory=list)
    income_bracket: Optional[str] = Field(None, pattern="^(Low|Middle|High)$")
    extracted_date: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "P001",
                "age": 52,
                "gender": "male",
                "location": "Mumbai, Maharashtra",
                "location_tier": "Tier 1",
                "conditions": ["Type 2 Diabetes Mellitus", "Hypertension"],
                "medications": [
                    {"name": "Metformin", "dose": "1000mg", "frequency": "BD", "duration_months": 60}
                ],
                "lab_values": {
                    "HbA1c": {"value": 8.7, "unit": "%", "date": "2025-01-15"}
                },
                "allergies": ["Penicillin"]
            }
        }


class ManualPatientInput(BaseModel):
    #Simplified patient input for manual form entry
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., pattern="^(male|female|other)$")
    location: str
    location_tier: Optional[str] = Field("Tier 1", pattern="^(Tier 1|Tier 2|Tier 3)$")
    primary_condition: str
    additional_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    hba1c: Optional[float] = Field(None, ge=0, le=20)
    blood_pressure_systolic: Optional[int] = Field(None, ge=60, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=150)
    income_bracket: Optional[str] = Field(None, pattern="^(Low|Middle|High)$")
    
    def to_patient_profile(self) -> PatientProfile:
        #Convert manual input to full patient profile
        conditions = [self.primary_condition] + self.additional_conditions
        
        medications = [
            Medication(name=med) for med in self.current_medications
        ]
        
        lab_values = {}
        if self.hba1c:
            lab_values["HbA1c"] = LabValue(value=self.hba1c, unit="%")
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            lab_values["blood_pressure"] = LabValue(
                value=self.blood_pressure_systolic,
                unit="mmHg"
            )
        
        return PatientProfile(
            age=self.age,
            gender=self.gender,
            location=self.location,
            location_tier=self.location_tier,
            conditions=conditions,
            medications=medications,
            lab_values=lab_values,
            income_bracket=self.income_bracket
        )


class PatientExtractionResult(BaseModel):
    #Result of AI extraction from patient documents
    success: bool
    profile: Optional[PatientProfile] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    extraction_time_seconds: Optional[float] = None

class UploadAndMatchResult(BaseModel):
    #Combined result of upload, extraction, and trial matching
    extraction: PatientExtractionResult
    matching: Optional[Dict[str, Any]] = None
    total_time_seconds: Optional[float] = None