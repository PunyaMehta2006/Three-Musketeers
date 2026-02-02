"""
File handling utilities for uploads
"""
import os
import shutil
from typing import Optional
from fastapi import UploadFile
# Upload directory
UPLOAD_DIR = os.path.join(
    os.path.dirname(__file__),
    "../../uploads"
)
async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to uploads directory
    
    Args:
        upload_file: FastAPI UploadFile object
    
    Returns:
        Absolute path to saved file
    """
    # Ensure uploads directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Create file path
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path
def delete_file(file_path: str) -> bool:
    """
    Delete a file if it exists
    
    Args:
        file_path: Path to file to delete
    
    Returns:
        True if deleted, False if file didn't exist
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False