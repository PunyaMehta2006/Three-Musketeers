import time
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
from app.models.patient import CompleteWorkflowResult, PatientExtractionResult, TrialWithAnalysis
from app.agents import (
    extract_patient_profile,
    search_trials_for_patient,
    check_eligibility,
    calculate_diversity_score,
    generate_explanation
)
from app.utils.file_helpers import save_upload_file, delete_file
router = APIRouter(prefix="/api", tags=["complete-workflow"])
@router.post("/complete-workflow", response_model=CompleteWorkflowResult)
async def complete_workflow(file: UploadFile = File(...)):
    """
    Complete patient analysis workflow - All 5 agents
    
    Flow:
    1. Agent 1: Extract patient profile from document
    2. Agent 2: Search matching trials
    3. For each trial:
       - Agent 3: Check eligibility
       - Agent 5: Calculate diversity score
       - Agent 4: Generate explanation
    
    Args:
        file: Medical record file (PDF, JPG, PNG)
    
    Returns:
        CompleteWorkflowResult with all agent outputs
    """
    start_time = time.time()
    
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: PDF, JPG, PNG"
        )
    
    # Save uploaded file temporarily
    file_path = await save_upload_file(file)
    
    try:
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        # AGENT 1: PROFILE EXTRACTION
        print("🤖 Agent 1: Extracting patient profile...")
        extraction_result = await extract_patient_profile(file_path, file_ext)
        
        if not extraction_result.success or not extraction_result.profile:
            # Return early if extraction failed
            return CompleteWorkflowResult(
                extraction=extraction_result,
                total_trials_found=0,
                trials_checked=0,
                eligible_count=0,
                possibly_eligible_count=0,
                not_eligible_count=0,
                trials=[],
                processing_time_seconds=round(time.time() - start_time, 2)
            )
        
        patient_profile = extraction_result.profile
        print(f"✅ Patient profile extracted: Age={patient_profile.age}, Conditions={patient_profile.conditions}")
        
        # AGENT 2: TRIAL SEARCH
        print("🔍 Agent 2: Searching matching trials...")
        trials = await search_trials_for_patient(patient_profile, max_results=1)
        total_trials = len(trials)
        print(f"✅ Found {total_trials} matching trials")
        
        if total_trials == 0:
            return CompleteWorkflowResult(
                extraction=extraction_result,
                total_trials_found=0,
                trials_checked=0,
                eligible_count=0,
                possibly_eligible_count=0,
                not_eligible_count=0,
                trials=[],
                processing_time_seconds=round(time.time() - start_time, 2)
            )
        
        # ========== AGENTS 3, 4, 5: PROCESS EACH TRIAL ==========
        print(f"🧬 Processing {total_trials} trials through Agents 3-5...")
        
        enriched_trials = []
        eligible_count = 0
        possibly_eligible_count = 0
        not_eligible_count = 0
        
        # Convert patient profile to dictionary for agents
        patient_dict = patient_profile.dict()
        
        for idx, trial in enumerate(trials):
            print(f"  Processing trial {idx+1}/{total_trials}: {trial.nct_id}")
            
            trial_dict = trial.dict()
            
            # Agent 3: Check Eligibility
            eligibility_result = await check_eligibility(patient_dict, trial_dict)
            
            # Count eligibility status
            status = eligibility_result.get("status", "POSSIBLY_ELIGIBLE")
            if status == "ELIGIBLE":
                eligible_count += 1
            elif status == "POSSIBLY_ELIGIBLE":
                possibly_eligible_count += 1
            else:
                not_eligible_count += 1
            
            # Agent 5: Calculate Diversity Score
            diversity_result = calculate_diversity_score(
                patient=patient_dict,
                trial=trial_dict,
                base_score=85  # Start with base eligibility score
            )
            
            # Agent 4: Generate Explanation
            explanation_result = generate_explanation(
                trial=trial_dict,
                eligibility=eligibility_result,
                diversity=diversity_result
            )
            
            # Combine all results
            enriched_trial = TrialWithAnalysis(
                nct_id=trial.nct_id,
                title=trial.title,
                brief_summary=trial.brief_summary,
                status=trial.status,
                phase=trial.phase,
                conditions=trial.conditions,
                locations=trial.locations,
                sponsor=trial.sponsor,
                minimum_age=trial.minimum_age,
                maximum_age=trial.maximum_age,
                gender=trial.gender,
                eligibility_criteria=trial.eligibility_criteria,
                eligibility=eligibility_result,
                diversity=diversity_result,
                explanation=explanation_result
            )
            
            enriched_trials.append(enriched_trial)
        
        print(f"✅ Processed all trials: {eligible_count} eligible, {possibly_eligible_count} possibly, {not_eligible_count} not eligible")
        
        # Sort by diversity score (highest first)
        enriched_trials.sort(
            key=lambda t: t.diversity.get("final_score", 0) if t.diversity else 0,
            reverse=True
        )
        
        # Calculate total time
        total_time = time.time() - start_time
        
        return CompleteWorkflowResult(
            extraction=extraction_result,
            total_trials_found=total_trials,
            trials_checked=total_trials,
            eligible_count=eligible_count,
            possibly_eligible_count=possibly_eligible_count,
            not_eligible_count=not_eligible_count,
            trials=enriched_trials,
            processing_time_seconds=round(total_time, 2)
        )
    
    finally:
        # Clean up uploaded file
        delete_file(file_path)