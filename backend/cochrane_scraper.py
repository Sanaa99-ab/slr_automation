# cochrane_scraper.py
import re
import csv
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from config import config 
from webdriver_manager.chrome import ChromeDriverManager


def debug_print(msg):
    print(f"[DEBUG] {msg}")

def clean_field(text, label):
    """
    Remove a leading label and an optional count (e.g. "Population (5)")
    from the field text.
    """
    pattern = re.compile(rf"^{label}\s*\(\d+\)\s*", re.IGNORECASE)
    return pattern.sub("", text).strip()

def extract_pico_from_iframe(soup):
    """
    Extract PICO details from the iframe page.
    Looks for the container with class "sc-htoDjs doGvts" and then extracts
    Population, Intervention, Comparison, and Outcome from the first 4 divs.
    """
    debug_print("Extracting PICO data from iframe soup.")
    container = soup.find("div", class_="sc-htoDjs doGvts")
    if container:
        info_divs = container.find_all("div", class_="sc-dnqmqq efKoYv")
        debug_print(f"Found {len(info_divs)} PICO info divs.")
        if len(info_divs) >= 4:
            pico = {
                "population": clean_field(info_divs[0].get_text(strip=True), "Population"),
                "intervention": clean_field(info_divs[1].get_text(strip=True), "Intervention"),
                "comparison": clean_field(info_divs[2].get_text(strip=True), "Comparison"),
                "outcome": clean_field(info_divs[3].get_text(strip=True), "Outcome")
            }
            debug_print(f"Extracted PICO: {pico}")
            return pico
    debug_print("PICO container not found or insufficient data.")
    return None

def get_next_page_url(soup):
    """
    Parse the pagination section in the footer and return the URL for the next page.
    """
    footer_div = soup.find("div", class_="search-results-footer")
    if not footer_div:
        return None
    pagination_div = footer_div.find("div", class_="pagination-page-links")
    if not pagination_div:
        return None
    ul_list = pagination_div.find("ul", class_="pagination-page-list")
    if not ul_list:
        return None
    active_li = ul_list.find("li", class_="pagination-page-list-item active")
    if not active_li:
        return None
    next_li = active_li.find_next_sibling("li", class_="pagination-page-list-item")
    if not next_li:
        return None
    next_a = next_li.find("a", href=True)
    if not next_a:
        return None
    return next_a["href"]

def scrape_search_page(query, max_reviews=None):
    """
    Loads the search results pages from the Cochrane Library using the passed query,
    and extracts for each review:
      - Title, Authors, Article URL, and PICO data (extracted via an iframe if available).
    Pagination is handled until 'max_reviews' records are collected.
    """
    if max_reviews is None:
        max_reviews = config.COCHRANE_MAX_REVIEWS

    base_url = config.COCHRANE_SEARCH_BASE_URL
    collected_records = []
    params = {
        "p_p_id": "scolarissearchresultsportlet_WAR_scolarissearchresults",
        "p_p_lifecycle": "0",
        "_scolarissearchresultsportlet_WAR_scolarissearchresults_searchType": "basic",
        "_scolarissearchresultsportlet_WAR_scolarissearchresults_searchBy": "6",
        # Pass the query inside a wildcard search
        "_scolarissearchresultsportlet_WAR_scolarissearchresults_searchText": f"*{query}"
    }
    # Prepare the search URL
    search_url = requests.Request('GET', base_url, params=params).prepare().url
    debug_print(f"Search URL: {search_url}")
    driver.get(search_url)
    page = 1

    while len(collected_records) < max_reviews:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-item"))
            )
        except Exception as e:
            debug_print(f"Error waiting for search results: {e}")
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        review_items = soup.find_all("div", class_="search-results-item")
        debug_print(f"Found {len(review_items)} review items on page {page}.")
        if not review_items:
            break

        for item in review_items:
            if len(collected_records) >= max_reviews:
                break
            title_tag = item.find("h3", class_="result-title")
            if not title_tag or not title_tag.find("a"):
                continue
            title = title_tag.find("a").get_text(strip=True)
            href = title_tag.find("a").get("href")
            # Verify that the URL contains the proper path indicating a review in Cochrane (e.g., "/cdsr/")
            if not (href and "/cdsr/" in href):
                continue
            article_url = "https://www.cochranelibrary.com" + href + "/full"
            authors_tag = item.find("div", class_="search-result-authors")
            authors = authors_tag.get_text(strip=True) if authors_tag else "N/A"

            pico = "N/A"
            pico_iframe_url = "N/A"
            pico_container = item.find("div", class_="search-result-picos")
            if pico_container:
                iframes = pico_container.find_all("iframe")
                for iframe in iframes:
                    src = iframe.get("src", "")
                    debug_print(f"Found iframe src: {src}")
                    if "cochrane.org/assets/pico-data" in src:
                        if "requestDataFromParent=true" in src:
                            src = src.replace("requestDataFromParent=true", "requestDataFromParent=false")
                        pico_iframe_url = src
                        break

            if pico_iframe_url != "N/A":
                if not pico_iframe_url.startswith("http"):
                    pico_iframe_url = "https://www.cochranelibrary.com" + pico_iframe_url
                debug_print(f"Opening PICO iframe: {pico_iframe_url}")
                try:
                    window_before = driver.current_window_handle
                    driver.execute_script("window.open(arguments[0]);", pico_iframe_url)
                    sleep(2)
                    window_after = driver.window_handles[-1]
                    driver.switch_to.window(window_after)
                except Exception as e:
                    debug_print(f"Error opening or switching to PICO iframe tab: {e}")
                    traceback.print_exc()
                    continue
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-htoDjs.doGvts"))
                    )
                except Exception as e:
                    debug_print(f"Error waiting for nested PICO container: {e}")
                    debug_print("Iframe page source snippet: " + driver.page_source[:500])
                    driver.close()
                    driver.switch_to.window(window_before)
                    continue
                iframe_soup = BeautifulSoup(driver.page_source, "html.parser")
                pico_extracted = extract_pico_from_iframe(iframe_soup)
                pico = pico_extracted if pico_extracted else "N/A"
                try:
                    driver.close()
                    driver.switch_to.window(window_before)
                except Exception as e:
                    debug_print(f"Error closing tab or switching back: {e}")
                    traceback.print_exc()
            record = {
                "title": title,
                "authors": authors,
                "article_url": article_url,
                "pico": pico,
                "pico_url": pico_iframe_url
            }
            debug_print(f"Record extracted: {record}")
            collected_records.append(record)
        debug_print(f"Collected {len(collected_records)} records so far on page {page}.")
        if len(collected_records) >= max_reviews:
            break
        next_page_link = get_next_page_url(soup)
        if not next_page_link:
            debug_print("No next page link found; ending pagination.")
            break
        if not next_page_link.startswith("http"):
            next_page_link = "https://www.cochranelibrary.com" + next_page_link
        debug_print(f"Navigating to next page: {next_page_link}")
        driver.get(next_page_link)
        sleep(2)
        page += 1

    return collected_records[:max_reviews]

def scrape_complete_review(article_url):
    """
    Visits the article page and extracts the complete review content from the abstract.
    The function concatenates subsections (titles and paragraphs) into one string.
    """
    debug_print(f"Scraping complete review from article: {article_url}")
    try:
        driver.get(article_url)
        sleep(2)
    except Exception as e:
        debug_print(f"Error loading article URL: {e}")
        return "N/A"
    page_soup = BeautifulSoup(driver.page_source, "html.parser")
    abstract_div = page_soup.find("div", class_="abstract full_abstract")
    if not abstract_div:
        debug_print("Abstract container not found.")
        return "N/A"
    subsections = abstract_div.find_all(["div", "section"], recursive=False)
    debug_print(f"Found {len(subsections)} abstract subsections.")
    complete_review = ""
    for sec in subsections:
        h3 = sec.find("h3")
        p = sec.find("p")
        if h3 and p:
            complete_review += h3.get_text(strip=True) + "\n" + p.get_text(strip=True) + "\n\n"
        else:
            complete_review += sec.get_text(separator="\n", strip=True) + "\n\n"
    return complete_review.strip() if complete_review.strip() != "" else "N/A"

# Initialize the Selenium WebDriver using config parameters
# def init_driver():
#     chrome_options = Options()
#     if config.HEADLESS_BROWSER:
#         chrome_options.add_argument('--headless')
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     try:
#         # Use Selenium 4's Service wrapper for ChromeDriver
#         from selenium.webdriver.chrome.service import Service
#         service = Service(config.CHROME_DRIVER_PATH)
#         return webdriver.Chrome(service=service, options=chrome_options)
#     except Exception as e:
#         debug_print(f"Error initializing ChromeDriver: {e}")
#         raise

# # Create the driver instance once when the module is imported.
# driver = init_driver()

def init_driver():
    chrome_options = Options()
    if config.HEADLESS_BROWSER:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    try:
        # Create a Service with the proper executable path from ChromeDriverManager.
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error initializing ChromeDriver: {e}")
        raise

# Then replace your driver initialization with:
driver = init_driver()

def main():
    # Accept a topic dynamically (for testing, we use a default value)
    query = "diabetes treatment"  # In production, this will come dynamically from the form input.
    debug_print("Starting scrape of search results...")
    # Use the maximum reviews number from the configuration
    records = scrape_search_page(query, max_reviews=config.COCHRANE_MAX_REVIEWS)
    debug_print(f"Scraped {len(records)} review records from search results.")

    # For each record, scrape the complete review content from the article page.
    for idx, record in enumerate(records, 1):
        debug_print(f"Scraping complete review for article {idx}: {record['article_url']}")
        complete_review = scrape_complete_review(record["article_url"])
        record["complete_review"] = complete_review
        debug_print(f"Complete review length: {len(complete_review)} characters")
        sleep(1)
    
    csv_filename = f"cochrane_results_{query.replace(' ', '_')}.csv"
    save_records_to_csv(records, csv_filename)

    # For now, simply print the scraped records; later you can integrate these into your platform's table
    for rec in records:
        print(rec)


def save_records_to_csv(records, filename):
    # Define CSV field names; adjust these to match the keys in your record dictionaries.
    fieldnames = ["title", "authors", "article_url", "pico", "pico_url", "complete_review"]
    
    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                # If the 'pico' field is a dictionary, convert it to a string.
                if isinstance(rec.get("pico"), dict):
                    pico_str = ", ".join([f"{k}: {v}" for k, v in rec["pico"].items()])
                else:
                    pico_str = rec.get("pico", "N/A")
                
                row = {
                    "title": rec.get("title"),
                    "authors": rec.get("authors"),
                    "article_url": rec.get("article_url"),
                    "pico": pico_str,
                    "pico_url": rec.get("pico_url", "N/A"),
                    "complete_review": rec.get("complete_review", "N/A")
                }
                writer.writerow(row)
        print(f"Records successfully saved to {filename}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        debug_print(f"Fatal error: {e}")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception as e:
            debug_print(f"Error quitting driver: {e}")
