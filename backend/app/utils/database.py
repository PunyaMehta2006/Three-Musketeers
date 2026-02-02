"""
Database utilities for clinical trials
Handles SQLite connection and queries
"""
import aiosqlite
import os
import json
from typing import List, Dict, Optional
# Database location
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "../../../data/trials.db"
)
async def init_db():
    """
    Initialize the database - creates trials table if it doesn't exist
    Safe to run multiple times
    """
    # Create data folder if needed
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Connect to database
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Create trials table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trials (
                nct_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                brief_summary TEXT,
                status TEXT,
                phase TEXT,
                conditions TEXT,
                eligibility_criteria TEXT,
                minimum_age TEXT,
                maximum_age TEXT,
                gender TEXT,
                locations TEXT,
                sponsor TEXT
            )
        """)
        
        await db.commit()
        print("[*] Database initialized")
async def get_trial_count() -> int:
    """Get total number of trials in database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM trials")
        row = await cursor.fetchone()
        return row[0] if row else 0
async def search_trials_by_condition(
    conditions: List[str], 
    location: Optional[str] = None, 
    limit: int = 50
) -> List[Dict]:
    """
    Search for trials matching patient conditions
    
    Args:
        conditions: List of patient conditions
        location: Optional location filter
        limit: Max number of results
    
    Returns:
        List of trial dictionaries
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Return results as dictionaries
        db.row_factory = aiosqlite.Row
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        for condition in conditions:
            where_clauses.append("LOWER(conditions) LIKE ?")
            params.append(f"%{condition.lower()}%")
        
        # Combine with OR
        where_sql = " OR ".join(where_clauses) if where_clauses else "1=1"
        
        # Build query
        query = f"""
            SELECT * FROM trials 
            WHERE ({where_sql}) 
            AND status = 'RECRUITING'
            LIMIT ?
        """
        params.append(limit)
        
        # Execute
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Convert to list of dicts
        trials = []
        for row in rows:
            trial = dict(row)
            
            # Parse JSON fields
            if trial.get("conditions"):
                try:
                    trial["conditions"] = json.loads(trial["conditions"])
                except:
                    trial["conditions"] = [trial["conditions"]]
            
            if trial.get("locations"):
                try:
                    trial["locations"] = json.loads(trial["locations"])
                except:
                    trial["locations"] = [trial["locations"]]
            
            trials.append(trial)
        
        return trials
async def insert_trial(trial_data: Dict):
    """Insert a single trial into database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO trials 
            (nct_id, title, brief_summary, status, phase, conditions,
             eligibility_criteria, minimum_age, maximum_age, gender,
             locations, sponsor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trial_data.get("nct_id"),
            trial_data.get("title"),
            trial_data.get("brief_summary"),
            trial_data.get("status"),
            trial_data.get("phase"),
            json.dumps(trial_data.get("conditions", [])),
            trial_data.get("eligibility_criteria"),
            trial_data.get("minimum_age"),
            trial_data.get("maximum_age"),
            trial_data.get("gender"),
            json.dumps(trial_data.get("locations", [])),
            trial_data.get("sponsor")
        ))
        await db.commit()