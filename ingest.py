# ingest.py
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from config import ARXIV_API_URL

def fetch_arxiv_data(topic: str, max_results: int = 20) -> pd.DataFrame:
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results
    }
    response = requests.get(ARXIV_API_URL, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper_data = {
            'id': entry.find('{http://www.w3.org/2005/Atom}id').text,
            'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
            'published': entry.find('{http://www.w3.org/2005/Atom}published').text,
            'authors': [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
            'source': 'arxiv'
        }
        papers.append(paper_data)
        
    df = pd.DataFrame(papers)
    return df

if __name__ == "__main__":
    topic_of_interest = "quantum computing"
    print(f"Fetching latest papers on: '{topic_of_interest}'...")
    df = fetch_arxiv_data(topic=topic_of_interest)
    print(f"Successfully fetched {len(df)} papers.")
    print(df.head())