# config.py
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class Config:
    DATABASE = "PubMed"
    MAX_PAPERS = 3
    EMAIL = os.getenv("NCBI_EMAIL")  # Loaded from .env
    SUPPORTED_DATABASES = ["PubMed", "Scopus", "IEEE"]
    HF_API_KEY = os.getenv("HF_API_KEY")  # Loaded from .env
    HF_MODEL = "bigscience/bloom-560m"  # Still configurable here

config = Config()

# Validate critical variables
if not config.HF_API_KEY:
    raise ValueError("HF_API_KEY not set in .env file")
if not config.EMAIL:
    raise ValueError("NCBI_EMAIL not set in .env file")