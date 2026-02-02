"""
Trials routes - Database queries and trial information
"""
from fastapi import APIRouter
from app.utils.database import get_trial_count, search_trials_by_condition
from typing import List
router = APIRouter(prefix="/api/trials", tags=["trials"])
@router.get("/count")
async def get_total_trials():
    """
    Get total number of trials in database
    
    Returns:
        {"count": number_of_trials}
    """
    count = await get_trial_count()
    return {"count": count}
@router.get("/search")
async def search_trials(
    conditions: str,
    location: str = None,
    limit: int = 50
):
    """
    Search for trials by conditions
    
    Args:
        conditions: Comma-separated list of conditions
        location: Optional location filter
        limit: Max number of results (default 50)
    
    Returns:
        List of trials matching criteria
    """
    # Parse conditions
    condition_list = [c.strip() for c in conditions.split(",")]
    
    # Search database
    trials = await search_trials_by_condition(
        conditions=condition_list,
        location=location,
        limit=limit
    )
    
    return {
        "total": len(trials),
        "trials": trials
    }