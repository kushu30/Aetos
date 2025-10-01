# ingest_patents.py
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import os

def fetch_patent_data(topic: str, max_results: int = 10) -> pd.DataFrame:
    scraper_api_key = os.getenv("SCRAPER_API_KEY")
    if not scraper_api_key:
        print("Warning: SCRAPER_API_KEY not found. Patent search will be skipped.")
        return pd.DataFrame()

    # Target the main search results page, which is more stable
    formatted_topic = quote_plus(topic)
    target_url = f"https://patents.google.com/?q=({formatted_topic})&num={max_results}"
    
    scraper_url = f'http://api.scraperapi.com?api_key={scraper_api_key}&url={target_url}'
    
    try:
        response = requests.get(scraper_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching patent data via ScraperAPI: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'lxml')
    results = soup.select('article.search-result')
    
    patents = []
    for item in results:
        title_tag = item.select_one('h4[itemprop="title"]')
        snippet_tag = item.select_one('div.snippet')
        link_tag = item.select_one('a[href^="/patent/"]')
        date_tag = item.select_one('time[itemprop="filingDate"]')
        
        if not all([title_tag, snippet_tag, link_tag]):
            continue

        title = title_tag.get_text(strip=True)
        summary = snippet_tag.get_text(strip=True)
        patent_id = link_tag['href'].split('/')[2]
        filing_date = date_tag.get_text(strip=True) if date_tag else 'N/A'

        patents.append({
            'id': f"https://patents.google.com/patent/{patent_id}",
            'title': title,
            'summary': summary,
            'published': filing_date,
            'authors': [], 
            'source': 'google_patents'
        })

    return pd.DataFrame(patents)