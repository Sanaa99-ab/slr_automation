# scraper.py
from Bio import Entrez
import time
from config import config

def scrape_pubmed(query: str, max_results: int = config.MAX_PAPERS) -> list[dict]:
    Entrez.email = config.EMAIL
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        ids = record["IdList"]
        
        papers = []
        for pid in ids:
            handle = Entrez.efetch(db="pubmed", id=pid, rettype="abstract", retmode="text")
            abstract = handle.read().strip()
            papers.append({"id": pid, "abstract": abstract[:100] + "..." if len(abstract) > 100 else abstract})
            handle.close()
            time.sleep(1)
        return papers
    except Exception as e:
        return [{"id": "Error", "abstract": f"Scraping failed: {str(e)}"}]