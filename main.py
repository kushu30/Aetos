# main.py
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from ingest import fetch_arxiv_data
from ingest_patents import fetch_patent_data
from database import save_to_db
from intelligence import get_gemini_analysis

def analyze_document(row_tuple):
    """Helper function to process a single document row for concurrency."""
    index, row = row_tuple
    insights = get_gemini_analysis(row['summary'])
    return {**row.to_dict(), **insights}

def run_pipeline(topic: str, num_documents: int = 100):
    print(f"--- Starting AETOS Batch Intelligence Run for topic: '{topic}' ---")
    
    # We fetch a larger number of documents for a comprehensive database build
    max_per_source = num_documents // 2
    
    # 1. Fetch Data
    print(f"Fetching {max_per_source} documents each from arXiv and Patents...")
    arxiv_df = fetch_arxiv_data(topic, max_results=max_per_source)
    patents_df = fetch_patent_data(topic, max_results=max_per_source)
    combined_df = pd.concat([arxiv_df, patents_df], ignore_index=True)
    
    # 2. Pre-filter for high-quality documents
    MIN_SUMMARY_LENGTH = 150
    original_count = len(combined_df)
    combined_df = combined_df[combined_df['summary'].str.len() >= MIN_SUMMARY_LENGTH]
    print(f"Filtered {original_count} docs down to {len(combined_df)} high-quality candidates for analysis.")

    if combined_df.empty:
        print("No high-quality documents found. Exiting.")
        return
        
    # 3. Process documents concurrently
    all_insights = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor: # Kept low for free-tier
        results_iterator = executor.map(analyze_document, combined_df.iterrows())
        all_insights = list(tqdm(results_iterator, total=len(combined_df), desc="Analyzing Documents"))

    # 4. Save the enriched data
    if all_insights:
        processed_df = pd.DataFrame(all_insights)
        processed_df = processed_df[processed_df['TRL'] != 0] # Filter out failed analyses
        if not processed_df.empty:
            print(f"Saving {len(processed_df)} successfully analyzed documents to the database.")
            save_to_db(processed_df)
    
    print("--- AETOS Batch Run Finished ---")

if __name__ == "__main__":
    # This script is now used to build our historical database, topic by topic.
    topic_of_interest = "quantum cryptography"
    run_pipeline(topic=topic_of_interest, num_documents=20)