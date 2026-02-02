"""
Upload routes - Handle file uploads and patient profile extraction
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import PatientExtractionResult, ManualPatientInput, PatientProfile
from app.agents import extract_patient_profile
from app.utils.file_helpers import save_upload_file, delete_file
router = APIRouter(prefix="/api", tags=["upload"])
@router.post("/upload", response_model=PatientExtractionResult)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a medical record (PDF or image) and extract patient profile
    
    Returns:
        PatientExtractionResult with extracted patient data
    """
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
    
        # Extract patient profile using Agent 1
        result = await extract_patient_profile(file_path, file_ext)
    
        return result
    
    finally:
        # Clean up uploaded file
        delete_file(file_path)
@router.post("/manual-input", response_model=PatientProfile)
async def manual_patient_input(form_data: ManualPatientInput):
    """
    Create patient profile from manual form input
    
    Args:
        form_data: ManualPatientInput with basic patient info
    
    Returns:
        Full PatientProfile
    """
    # Convert manual input to full patient profile
    profile = form_data.to_patient_profile()
    
    return profile