import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Search Service",
    description="A service for searching the web using DuckDuckGo",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SearchRequest(BaseModel):
    query: str
    max_results: int = 5
    region: str = "wt-wt"
    safesearch: str = "moderate"
    timelimit: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    href: str
    body: str

class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.get("/")
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Search Service API",
        "endpoints": {
            "/search": "Search the web using DuckDuckGo"
        }
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Search the web using DuckDuckGo"""
    try:
        # Initialize DuckDuckGo search
        ddgs = DDGS()
        
        # Perform the search
        results = ddgs.text(
            keywords=request.query,
            region=request.region,
            safesearch=request.safesearch,
            timelimit=request.timelimit,
            max_results=request.max_results
        )
        
        # Format the response
        search_results = []
        for result in results:
            search_result = SearchResult(
                title=result.get("title", ""),
                href=result.get("href", ""),
                body=result.get("body", "")
            )
            search_results.append(search_result)
        
        return SearchResponse(results=search_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching the web: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
