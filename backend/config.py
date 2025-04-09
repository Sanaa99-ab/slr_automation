# config.py
# from dotenv import load_dotenv
# import os

# load_dotenv()

# class Config:
#     DATABASE = "PubMed"  # Default for scraping (later)
#     MAX_PAPERS = 3
#     EMAIL = os.getenv("NCBI_EMAIL")
#     SUPPORTED_DATABASES = ["PubMed", "Scopus", "arXiv", "Google Scholar"]  # Predefined list
#     GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
#     OPENAI_MODEL = "gpt-4o"
#     OPENAI_BASE_URL = "https://models.inference.ai.azure.com"

# config = Config()

# if not config.GITHUB_TOKEN:
#     raise ValueError("GITHUB_TOKEN not set in .env file")
# if not config.EMAIL:
#     raise ValueError("NCBI_EMAIL not set in .env file")
# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Default database used for scraping (can be updated dynamically later)
    DEFAULT_DATABASE = "PubMed"
    MAX_PAPERS = 3
    EMAIL = os.getenv("NCBI_EMAIL")
    # Supported databases now includes Cochrane
    SUPPORTED_DATABASES = ["PubMed", "Scopus", "arXiv", "Google Scholar", "Cochrane"]
    
    # API and authentication configuration for OpenAI/GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_MODEL = "gpt-4o"
    OPENAI_BASE_URL = "https://models.inference.ai.azure.com"
    
    # New configuration for the Cochrane scraper
    COCHRANE_SEARCH_BASE_URL = "https://www.cochranelibrary.com/search"
    COCHRANE_MAX_REVIEWS = 5  # Maximum number of reviews to scrape for Cochrane
    # Specify the path to the ChromeDriver if necessary (or leave as "chromedriver" if it’s in your PATH)
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "chromedriver")
 
    # Whether to run the browser in headless mode
    HEADLESS_BROWSER = True

config = Config()

if not config.GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not set in .env file")
if not config.EMAIL:
    raise ValueError("NCBI_EMAIL not set in .env file")
