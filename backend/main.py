import os
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import config  
from llm import generate_research_questions, generate_search_queries, propose_criteria 
from scraper import scrape_pubmed 

class GenerateRequest(BaseModel):
    topic: str

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)
# build_dir = os.path.join(os.path.dirname(__file__), "../frontend/build")
# # Option with html=True so that unmatched routes serve index.html
# app.mount("/", StaticFiles(directory=build_dir, html=True), name="build")
# Calculate the path to the build folder
build_dir = os.path.join(os.path.dirname(__file__), "../frontend/build")
# Mount the build folder on a sub-path, e.g., "/app"
app.mount("/app", StaticFiles(directory=build_dir, html=True), name="app")


@app.post("/api/generate")
async def generate_slr(data: GenerateRequest):
    topic = data.topic
    questions = generate_research_questions(topic)
    queries = generate_search_queries(questions)
    databases = config.SUPPORTED_DATABASES
    criteria = propose_criteria(topic)
    query = queries[0] if queries else "AI AND education"
    papers = scrape_pubmed(query)
    return {
        "questions": questions,
        "queries": queries,
        "databases": databases,
        "criteria": criteria,
        "papers": papers
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)