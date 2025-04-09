import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from config import config  
from llm import generate_research_questions, generate_search_queries, propose_criteria 
from cochrane_scraper import scrape_search_page, scrape_complete_review, debug_print
from scraper import scrape_pubmed 

# class GenerateRequest(BaseModel):
#     topic: str


app = FastAPI()
# Add CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# build_dir = os.path.join(os.path.dirname(__file__), "../frontend/build")
# if os.path.exists(build_dir):
#     app.mount("/", StaticFiles(directory=build_dir, html=True), name="build")
# else:
#     @app.get("/")
#     def read_root():
#         return {"message": "Welcome to the SLR Automation API"}
build_dir = os.path.join(os.path.dirname(__file__), "../frontend/build")
if os.path.exists(build_dir):
    app.mount("/app", StaticFiles(directory=build_dir, html=True), name="build")
else:
    @app.get("/")
    def read_root():
        return {"message": "Welcome to the SLR Automation API"}


# Pydantic models
class TopicRequest(BaseModel):
    topic: str

class QuestionsRequest(BaseModel):
    topic: Optional[str] = None
    questions: list[str]
    

    
# Endpoint to generate research questions
@app.post("/api/generate-questions")
async def api_generate_questions(request: TopicRequest):
    questions = generate_research_questions(request.topic)
    return {"questions": questions}

# Endpoint to generate search queries based on questions
@app.post("/api/generate-queries")
async def api_generate_queries(request: QuestionsRequest):
    queries = generate_search_queries(request.topic, request.questions)
    return {"queries": queries}

@app.post("/api/scrape-cochrane")
async def scrape_cochrane(request: TopicRequest):
    try:
        records = scrape_search_page(request.topic, max_reviews=config.COCHRANE_MAX_REVIEWS)
        for idx, record in enumerate(records, 1):
            debug_print(f"Scraping complete review for article {idx}: {record['article_url']}")
            complete_review = scrape_complete_review(record["article_url"])
            record["complete_review"] = complete_review
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to propose inclusion/exclusion criteria
@app.post("/api/propose-criteria")
async def api_propose_criteria(request: TopicRequest):
    criteria = propose_criteria(request.topic)
    return {"criteria": criteria}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
    
    

