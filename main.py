# main.py
"""
Run a one-off pipeline locally (non-Celery) that fetches documents, runs
analysis concurrently (limited threads) and saves results to DB. Useful
for building initial historical DB.
"""

import pandas as pd
import concurrent.futures
from tqdm import tqdm
from ingest import fetch_arxiv_data
from ingest_patents import fetch_patent_data
from database import save_to_db
from intelligence import get_gemini_analysis

def analyze_document(row_tuple):
    """Helper for ThreadPoolExecutor - expects (index, Series) tuple."""
    _, row = row_tuple
    try:
        if len(row['summary'].split()) < 25:
            return {**row.to_dict(), "TRL": 0, "strategic_summary": "Skipped: Abstract too short."}
        insights = get_gemini_analysis(row['summary'])
        merged = row.to_dict()
        if isinstance(insights, dict):
            merged.update(insights)
        return merged
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return {**row.to_dict(), "TRL": 0}

def run_pipeline(topic: str, num_documents: int = 20):  # Increased default
    print(f"--- Starting AETOS Batch Intelligence Run for topic: '{topic}' ---")

    max_per_source = max(1, num_documents // 2)

    print(f"Fetching up to {max_per_source} documents each from arXiv and Patents...")
    arxiv_df = fetch_arxiv_data(topic, max_results=max_per_source)
    patents_df = fetch_patent_data(topic, max_results=max_per_source)

    if arxiv_df is None:
        arxiv_df = pd.DataFrame()
    if patents_df is None:
        patents_df = pd.DataFrame()

    combined_df = pd.concat([arxiv_df, patents_df], ignore_index=True, sort=False)

    # Parse published dates for sorting/filtering
    combined_df['published'] = pd.to_datetime(combined_df['published'], errors='coerce')

    MIN_SUMMARY_LENGTH = 150
    original_count = len(combined_df)
    combined_df = combined_df.dropna(subset=['summary'])
    combined_df = combined_df[combined_df['summary'].str.len() >= MIN_SUMMARY_LENGTH]
    print(f"Filtered {original_count} docs down to {len(combined_df)} high-quality candidates for analysis.")

    if combined_df.empty:
        print("No high-quality documents found. Exiting.")
        return

    # Concurrency: keep a small thread pool to avoid overwhelming the LLM or system
    all_insights = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results_iterator = executor.map(analyze_document, combined_df.iterrows())
        all_insights = list(tqdm(results_iterator, total=len(combined_df), desc="Analyzing Documents"))

    if all_insights:
        processed_df = pd.DataFrame(all_insights)
        processed_df = processed_df[processed_df.get('TRL', 0) != 0]
        if not processed_df.empty:
            print(f"Saving {len(processed_df)} successfully analyzed documents to the database.")
            save_to_db(processed_df)

    print("--- AETOS Batch Run Finished ---")

if __name__ == "__main__":
    topic_of_interest = "quantum cryptography"
    run_pipeline(topic=topic_of_interest, num_documents=5)