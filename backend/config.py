# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DATABASE = "PubMed"  # Default for scraping (later)
    MAX_PAPERS = 3
    EMAIL = os.getenv("NCBI_EMAIL")
    SUPPORTED_DATABASES = ["PubMed", "Scopus", "arXiv", "Google Scholar"]  # Predefined list
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_MODEL = "gpt-4o"
    OPENAI_BASE_URL = "https://models.inference.ai.azure.com"

config = Config()

if not config.GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not set in .env file")
if not config.EMAIL:
    raise ValueError("NCBI_EMAIL not set in .env file")