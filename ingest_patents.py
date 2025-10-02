import requests  # Fallback, but primary is Selenium
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_patent_data(topic: str, max_results: int = 10, retries: int = 3) -> pd.DataFrame:
    formatted_topic = quote_plus(topic)
    target_url = f"https://patents.google.com/?q=({formatted_topic})&num={max_results}"

    # Selenium setup (headless for efficiency)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    for attempt in range(1, retries + 1):
        try:
            print(f"Fetching patents for '{topic}' with Selenium (attempt {attempt})...")
            driver = webdriver.Chrome(options=options)
            driver.get(target_url)
            
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "search-result-item"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'lxml')
            results = soup.select('search-result-item')  # Container from SO/ common structure
            
            if not results:
                print("No results found. Trying fallback selectors.")
                results = soup.select('div.result') or soup.select('article') or []

            patents = []
            for item in results[:max_results]:
                # Title: h3 or a inside
                title_tag = item.select_one('h3 a') or item.select_one('a[href^="/patent/"] span')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)

                # Link
                link_tag = item.select_one('a[href^="/patent/"]')
                patent_url = f"https://patents.google.com{link_tag['href']}" if link_tag else ''

                # Summary/Snippet: span with abstract or description
                snippet_tag = item.select_one('span#htmlContent') or item.select_one('.snippet') or item.select_one('div.description')
                summary = snippet_tag.get_text(strip=True) if snippet_tag else ''

                # Date: h4.dates (from SO)
                date_tag = item.select_one('h4.dates')
                date_text = date_tag.get_text(strip=True) if date_tag else ''
                match = re.search(r'Publication date:\s*([\d-]+)', date_text)
                published = match.group(1) if match else 'N/A'

                # Authors/Inventors: From metadata h4 (from SO)
                authors = []
                metadata_tag = item.select_one('h4.metadata')
                if metadata_tag:
                    metadata_text = metadata_tag.get_text(strip=True)
                    inventor_match = re.search(r'Inventor[:\s]*(.+?)(?=,\s*Assignee|$)', metadata_text, re.IGNORECASE)
                    if inventor_match:
                        authors = [a.strip() for a in inventor_match.group(1).split(',')]

                patents.append({
                    'id': patent_url,
                    'title': title,
                    'summary': summary,
                    'published': published,
                    'authors': authors,
                    'source': 'google_patents'
                })

            print(f"Successfully fetched {len(patents)} patents.")

            # --- RELEVANCE VALIDATION STEP (matching arXiv) ---
            print(f"--- Relevance Check for Patents ---")
            relevant_patents = []
            topic_keywords = set(topic.lower().split())
            for p in patents:
                content = (p['title'] + ' ' + p['summary']).lower()
                if any(keyword in content for keyword in topic_keywords):
                    relevant_patents.append(p)
            
            print(f"--- Found {len(patents)} total patents, {len(relevant_patents)} are relevant. ---")
            time.sleep(3)
            return pd.DataFrame(relevant_patents)
            
        except Exception as e:
            print(f"Patent fetch attempt {attempt}/{retries} failed: {e}")
            if driver:
                driver.quit()
            if attempt < retries:
                sleep_time = 3 * attempt
                print(f"Retrying after {sleep_time}s...")
                time.sleep(sleep_time)

    if driver:
        driver.quit()
    print("All patent fetching attempts failed.")
    return pd.DataFrame()