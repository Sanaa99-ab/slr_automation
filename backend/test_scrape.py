# test_scraper.py
from cochrane_scraper import scrape_search_page, scrape_complete_review, debug_print, driver

def main():
    query = "diabetes treatment"  # Sample research query
    debug_print(f"Testing Cochrane scraper with query: {query}")
    
    # Scrape the search page for the given query, limiting to 5 records.
    records = scrape_search_page(query, max_reviews=5)
    print(f"Scraped {len(records)} records for query '{query}':\n")
    
    for idx, record in enumerate(records, 1):
        print(f"Record {idx}:")
        print("Title       :", record.get("title"))
        print("Authors     :", record.get("authors"))
        print("Article URL :", record.get("article_url"))
        print("PICO        :", record.get("pico"))
        print("PICO URL    :", record.get("pico_url"))
        
        # Optional: scrape the complete review (e.g., the abstract content)
        complete_review = scrape_complete_review(record.get("article_url"))
        # Print first 200 characters to avoid cluttering the console
        print("Complete Review (first 200 chars):", complete_review[:200], "...\n")
        print("-" * 80)
    
    # Quit the driver when done.
    driver.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        debug_print(f"An error occurred: {e}")
