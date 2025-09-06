from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.append('..')

from agents.agent_team import AgentTeam

app = FastAPI(title="Smart Search API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search system
search_system = AgentTeam()

class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default"

class SearchResponse(BaseModel):
    results: str
    confidence: float
    verification: str
    personalized: bool = False
    using_fallback: Optional[bool] = False
    optimized: Optional[bool] = False
    task_key: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Smart Search API is running!"}

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        # Execute search
        result = search_system.search(
            query=request.query,
            user_id=request.user_id
        )
        
        return SearchResponse(
            results=result["results"],
            confidence=result["confidence"],
            verification=result["verification"],
            personalized=result.get("personalized", False),
            using_fallback=result.get("using_fallback", False),
            optimized=result.get("optimized", False),
            task_key=result.get("task_key")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(user_id: str, result_id: str, feedback: str):
    """Track user clicks/feedback"""
    # Store feedback in user profile
    from agents.personalization import PersonalizationEngine
    personalization = PersonalizationEngine()
    personalization.update_profile(
        user_id,
        {"clicked_result": result_id, "feedback": feedback}
    )
    return {"status": "recorded"}

@app.get("/status")
async def get_status():
    """Get system status"""
    status = search_system.get_team_status()
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)