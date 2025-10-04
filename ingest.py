# ingest.py
import requests
import pandas as pd
from xml.etree import ElementTree as ET
import time

def fetch_arxiv_data(topic: str, max_results: int = 10) -> pd.DataFrame:
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    try:
        print(f"Fetching up to {max_results} arXiv papers for '{topic}'...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        all_papers = []
        for entry in root.findall('atom:entry', ns):
            paper_data = {
                'id': entry.find('atom:id', ns).text,
                'title': entry.find('atom:title', ns).text.strip(),
                'summary': entry.find('atom:summary', ns).text.strip(),
                'published': entry.find('atom:published', ns).text[:10],
                'authors': [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
                'source': 'arxiv',
                'provider_company': 'N/A'  # --- ADDED for data consistency
            }
            if all(paper_data.values()): # Basic check for missing fields
                all_papers.append(paper_data)
        
        # --- CRITICAL RELEVANCE VALIDATION STEP ---
        print(f"--- Relevance Check ---")
        relevant_papers = []
        topic_keywords = set(topic.lower().split())
        for paper in all_papers:
            content = (paper['title'] + ' ' + paper['summary']).lower()
            if any(keyword in content for keyword in topic_keywords):
                relevant_papers.append(paper)
        
        print(f"--- Found {len(all_papers)} total papers, {len(relevant_papers)} are relevant. ---")
        time.sleep(3)
        return pd.DataFrame(relevant_papers)
        
    except Exception as e:
        print(f"An error occurred in fetch_arxiv_data: {e}")
        return pd.DataFrame()