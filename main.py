# main.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from config import config
from llm import generate_research_questions, propose_criteria
from scraper import scrape_pubmed

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files

# Load HTML template
with open("templates/index.html", "r") as f:
    html_template = f.read()

@app.get("/", response_class=HTMLResponse)
async def get_form():
    return HTMLResponse(content=html_template.replace("{{ results|safe }}", ""))

@app.post("/", response_class=HTMLResponse)
async def process_form(topic: str = Form(...)):
    questions = generate_research_questions(topic)
    database = config.DATABASE
    criteria = propose_criteria(topic)
    query = questions[0].replace("What is", "").replace("?", "").strip()
    papers = scrape_pubmed(query)

    results_html = f"""
    <h2>Results</h2>
    <h3>Research Questions:</h3><ul>{''.join(f'<li>{q}</li>' for q in questions)}</ul>
    <h3>Selected Database:</h3><p>{database}</p>
    <h3>Proposed Criteria:</h3><ul>{''.join(f'<li>{c}</li>' for c in criteria)}</ul>
    <h3>Scraped Papers (Sample):</h3><ul>{''.join(f'<li>PMID: {p["id"]} - {p["abstract"]}</li>' for p in papers)}</ul>
    """
    return HTMLResponse(content=html_template.replace("{{ results|safe }}", results_html))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)