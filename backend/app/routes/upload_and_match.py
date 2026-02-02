"""
Upload and Match - Combined endpoint for file upload, extraction, and trial matching
"""
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.patient import UploadAndMatchResult, PatientExtractionResult
from app.agents import extract_patient_profile, search_trials_for_patient
from app.utils.file_helpers import save_upload_file, delete_file
router = APIRouter(prefix="/api", tags=["upload-and-match"])
@router.post("/upload-and-match", response_model=UploadAndMatchResult)
async def upload_and_match(file: UploadFile = File(...)):
    """
    Upload a medical record, extract patient profile, and match to trials - all in one call
    
    This combines Agent 1 (profile extraction) and Agent 2 (trial matching) into a single endpoint.
    
    Args:
        file: Medical record file (PDF, JPG, PNG)
    
    Returns:
        UploadAndMatchResult with extraction results and matched trials
    """
    # Start total timer
    start_time = time.time()
    
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: PDF, JPG, PNG"
        )
    
    # Save uploaded file
    file_path = await save_upload_file(file)
    
    try:
        # Get file extension with dot prefix (e.g., '.pdf', '.jpg')
        file_ext = '.' + file.filename.split('.')[-1].lower()
    
        # STEP 1: Extract patient profile using Agent 1
        extraction_result = await extract_patient_profile(file_path, file_ext)
        
        # STEP 2: Match trials using Agent 2 (only if extraction succeeded)
        matching_result = None
        if extraction_result.success and extraction_result.profile:
            try:
                # Search for matching trials
                trials = await search_trials_for_patient(extraction_result.profile)
                
                matching_result = {
                    "patient_age": extraction_result.profile.age,
                    "patient_gender": extraction_result.profile.gender,
                    "patient_conditions": extraction_result.profile.conditions,
                    "total_matches": len(trials),
                    "trials": [trial.dict() for trial in trials]
                }
            except Exception as e:
                matching_result = {
                    "error": f"Trial matching failed: {str(e)}",
                    "total_matches": 0,
                    "trials": []
                }
        
        # Calculate total time
        total_time = time.time() - start_time
        
        return UploadAndMatchResult(
            extraction=extraction_result,
            matching=matching_result,
            total_time_seconds=round(total_time, 2)
        )
    
    finally:
        # Clean up uploaded file
        delete_file(file_path)