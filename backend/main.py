"""
Three-Musketeers Backend API
Agents 1 & 2: Patient Profile Extraction and Trial Matching
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload_router, trials_router, matching_router , upload_and_match_router
from app.utils.database import init_db
# Create FastAPI app
app = FastAPI(
    title="Three-Musketeers Clinical Trials API",
    description="Backend API for patient profile extraction and trial matching",
    version="1.0.0"
)
# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register routers
app.include_router(upload_router)
app.include_router(trials_router)
app.include_router(matching_router)
app.include_router(upload_and_match_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print("✅ Server started - Database initialized")
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Three-Musketeers API - Agents 1 & 2",
        "agents": {
            "agent_1": "Profile Extractor",
            "agent_2": "Trial Searcher"
        }
    }
@app.get("/health")
async def health_check():
    """Detailed health check"""
    from app.utils.database import get_trial_count
    
    trial_count = await get_trial_count()
    
    return {
        "status": "healthy",
        "database": "connected",
        "trials_in_database": trial_count
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)