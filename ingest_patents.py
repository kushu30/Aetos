# ingest_patents.py
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def fetch_patent_data(topic: str, max_results: int = 10) -> pd.DataFrame:
    formatted_topic = quote_plus(topic)
    url = f"https://patents.google.com/xhr/query?url=q%3D{formatted_topic}&num={max_results}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching patent data: {e}")
        return pd.DataFrame()

    patents = []
    results = data.get('results', {}).get('cluster', [])
    if not results:
        return pd.DataFrame()

    for cluster in results[0].get('result', []):
        patent_info = cluster.get('patent', {})
        patent_id = patent_info.get('publication_number')
        
        # Extracting snippets can be complex, we'll simplify
        title = patent_info.get('title', 'No title available')
        summary = patent_info.get('snippet', 'No summary available')
        
        # Clean up the text which may contain HTML tags
        title = BeautifulSoup(title, 'lxml').get_text()
        summary = BeautifulSoup(summary, 'lxml').get_text()

        patent_data = {
            'id': f"https://patents.google.com/patent/{patent_id}",
            'title': title,
            'summary': summary,
            'published': patent_info.get('filing_date_str', 'N/A'),
            'authors': [inv.get('name', 'N/A') for inv in patent_info.get('inventor_harmonized', [])],
            'source': 'google_patents' # Add a field to distinguish data source
        }
        patents.append(patent_data)

    return pd.DataFrame(patents)

if __name__ == "__main__":
    topic_of_interest = "graphene sensor"
    print(f"Fetching latest patents on: '{topic_of_interest}'...")
    
    df = fetch_patent_data(topic=topic_of_interest)
    
    if not df.empty:
        print(f"Successfully fetched {len(df)} patents.")
        print("Sample data:")
        print(df.head())
    else:
        print("No patents found or error occurred.")