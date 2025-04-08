import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import argparse
import logging
from urllib.parse import urljoin

class CochraneScraper:
    def __init__(self, output_file="cochrane_slr_data.csv", log_level=logging.INFO):
        self.base_url = "https://www.cochranelibrary.com"
        self.search_url = f"{self.base_url}/advanced-search"
        self.output_file = output_file
        
        # Setup logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger("CochraneScraper")
        
        # Headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Initialize dataframe to store results
        self.results_df = pd.DataFrame(columns=[
            'title', 'authors', 'publication_date', 'doi', 'abstract', 
            'background', 'objectives', 'search_methods', 'selection_criteria',
            'data_collection', 'main_results', 'authors_conclusions', 'plain_language_summary',
            'query_term', 'url'
        ])
        
        self.logger.info("CochraneScraper initialized")
    
    def search(self, query, max_results=20):
        """
        Search for systematic reviews related to the query term
        """
        self.logger.info(f"Searching for: {query}")
        
        # Format query for Cochrane search
        formatted_query = query.replace(' ', '+')
        search_params = {
            'searchBy': '1',
            'searchText': formatted_query,
            'searchType': 'basic',
            'publishFrom': '',
            'publishTo': '',
            'accurateFrom': '',
            'accurateTo': '',
            'source': 'advanced',
            'selectedReviews': 'reviews',
            'reviewStatus': 'published'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search", 
                params=search_params,
                headers=self.headers
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find review links
            review_links = []
            articles = soup.select('article.search-results-item')
            
            for article in articles[:max_results]:
                link_element = article.select_one('h3.result-title a')
                if link_element and 'href' in link_element.attrs:
                    href = link_element['href']
                    full_url = urljoin(self.base_url, href)
                    review_links.append(full_url)
            
            self.logger.info(f"Found {len(review_links)} review links")
            return review_links
        
        except requests.RequestException as e:
            self.logger.error(f"Error searching Cochrane: {e}")
            return []
    
    def extract_review_data(self, url):
        """
        Extract data from a Cochrane systematic review page
        """
        self.logger.info(f"Extracting data from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {
                'title': self._get_text(soup, 'h1.publication-title'),
                'authors': self._get_text(soup, '.author-list'),
                'publication_date': self._get_text(soup, '.publication-date'),
                'doi': self._extract_doi(soup),
                'abstract': self._get_section_text(soup, 'Abstract'),
                'background': self._get_section_text(soup, 'Background'),
                'objectives': self._get_section_text(soup, 'Objectives'),
                'search_methods': self._get_section_text(soup, 'Search methods'),
                'selection_criteria': self._get_section_text(soup, 'Selection criteria'),
                'data_collection': self._get_section_text(soup, 'Data collection and analysis'),
                'main_results': self._get_section_text(soup, 'Main results'),
                'authors_conclusions': self._get_section_text(soup, "Authors' conclusions"),
                'plain_language_summary': self._get_section_text(soup, 'Plain language summary'),
                'url': url
            }
            
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"Error extracting review data: {e}")
            return None
    
    def _get_text(self, soup, selector):
        """Helper to extract text from an element"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
    
    def _get_section_text(self, soup, section_title):
        """Extract text from a specific section of the review"""
        # Find section heading
        section_heading = None
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            if section_title.lower() in heading.get_text().lower():
                section_heading = heading
                break
        
        if not section_heading:
            return ""
        
        # Get text from paragraphs following the heading until the next heading
        text = []
        current = section_heading.find_next()
        while current and current.name not in ['h2', 'h3', 'h4']:
            if current.name == 'p':
                text.append(current.get_text(strip=True))
            current = current.find_next()
        
        return " ".join(text)
    
    def _extract_doi(self, soup):
        """Extract DOI from the page"""
        doi_element = soup.select_one('.doi-link')
        if doi_element:
            doi_text = doi_element.get_text(strip=True)
            doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', doi_text, re.IGNORECASE)
            if doi_match:
                return doi_match.group(0)
        return ""
    
    def run(self, queries, max_results_per_query=5, delay=2):
        """
        Run the scraper for a list of healthcare queries
        """
        if isinstance(queries, str):
            queries = [queries]
        
        total_reviews = 0
        
        for query in queries:
            self.logger.info(f"Processing query: {query}")
            review_links = self.search(query, max_results=max_results_per_query)
            
            for link in review_links:
                # Add delay to be respectful to the server
                time.sleep(delay)
                
                data = self.extract_review_data(link)
                if data:
                    data['query_term'] = query
                    self.results_df = pd.concat([self.results_df, pd.DataFrame([data])], ignore_index=True)
                    total_reviews += 1
            
            self.logger.info(f"Processed {len(review_links)} reviews for query: {query}")
        
        self.logger.info(f"Completed processing {total_reviews} reviews across {len(queries)} queries")
        
        # Save results to CSV
        self.save_results()
        
        return self.results_df
    
    def save_results(self):
        """Save results to CSV file"""
        try:
            self.results_df.to_csv(self.output_file, index=False, encoding='utf-8')
            self.logger.info(f"Results saved to {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Cochrane systematic reviews for healthcare queries")
    parser.add_argument('--queries', nargs='+', required=True, help='Healthcare queries to search for')
    parser.add_argument('--output', default='cochrane_slr_data.csv', help='Output CSV file')
    parser.add_argument('--max-results', type=int, default=5, help='Maximum results per query')
    parser.add_argument('--delay', type=int, default=2, help='Delay between requests in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    scraper = CochraneScraper(
        output_file=args.output,
        log_level=logging.DEBUG if args.verbose else logging.INFO
    )
    
    scraper.run(args.queries, max_results_per_query=args.max_results, delay=args.delay)