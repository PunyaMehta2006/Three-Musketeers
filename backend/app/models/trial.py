"""
Clinical trial data models for DiversityMatch.AI
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Trial(BaseModel):
    """Clinical trial from database"""
    nct_id: str  # NCT number from ClinicalTrials.gov
    title: str
    brief_summary: Optional[str] = None
    detailed_description: Optional[str] = None
    status: str  # RECRUITING, COMPLETED, etc.
    phase: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)
    eligibility_criteria: Optional[str] = None
    minimum_age: Optional[str] = None
    maximum_age: Optional[str] = None
    gender: Optional[str] = None  # ALL, FEMALE, MALE
    locations: List[str] = Field(default_factory=list)
    sponsor: Optional[str] = None
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    enrollment: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nct_id": "NCT05123456",
                "title": "Study of Semaglutide in Type 2 Diabetes",
                "status": "RECRUITING",
                "phase": "Phase 3",
                "conditions": ["Type 2 Diabetes"],
                "eligibility_criteria": "Include: Age 18-65, HbA1c 7-10%...",
                "locations": ["Mumbai, India", "Delhi, India"]
            }
        }


class EligibilityCriterion(BaseModel):
    """Individual eligibility criterion result"""
    criterion: str
    patient_value: str
    status: str  # PASS, FAIL, MISSING, NOT_APPLICABLE
    reasoning: str


class MissingData(BaseModel):
    """Missing data that affects eligibility"""
    field: str
    reason: str
    impact: str  # CRITICAL, HIGH, MEDIUM, LOW


class EligibilityResult(BaseModel):
    """Result of eligibility check for a single trial"""
    status: str  # ELIGIBLE, NOT_ELIGIBLE, POSSIBLY_ELIGIBLE, ERROR
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    inclusion_criteria: List[EligibilityCriterion] = Field(default_factory=list)
    exclusion_criteria: List[EligibilityCriterion] = Field(default_factory=list)
    missing_data: List[MissingData] = Field(default_factory=list)
    error: Optional[str] = None


class DiversityReason(BaseModel):
    """Reason for diversity priority"""
    icon: str
    text: str
    weight: str  # HIGH, MEDIUM, LOW


class DiversityScore(BaseModel):
    """Diversity optimization score for a trial match"""
    final_score: float
    base_score: float
    diversity_boost: float
    diversity_reasons: List[DiversityReason] = Field(default_factory=list)
    priority_level: str  # HIGH, MEDIUM, STANDARD
    priority_label: str


class TrialMatch(BaseModel):
    """Complete trial match result with eligibility and diversity"""
    trial: Trial
    eligibility: EligibilityResult
    diversity: Optional[DiversityScore] = None
    simplified_summary: Optional[Dict[str, Any]] = None


class TrialSearchResult(BaseModel):
    """Result of trial search"""
    patient_id: str
    total_trials_checked: int
    eligible_trials: int
    high_priority: List[TrialMatch] = Field(default_factory=list)
    medium_priority: List[TrialMatch] = Field(default_factory=list)
    standard: List[TrialMatch] = Field(default_factory=list)
    processing_time_seconds: float


class TrialSimplifiedSummary(BaseModel):
    """Patient-friendly trial summary"""
    what_tested: str
    who_can_join: str
    time_commitment: str
    location: List[str]
    what_you_get: str
