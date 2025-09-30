# main.py
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from ingest import fetch_arxiv_data
from ingest_patents import fetch_patent_data
from database import save_to_db
from intelligence import get_gemini_analysis

def analyze_document(row_tuple):
    index, row = row_tuple
    insights = get_gemini_analysis(row['summary'])
    return {**row.to_dict(), **insights}

def run_pipeline(topic: str, max_results_per_source: int = 15):
    print(f"--- Starting AETOS Pipeline for topic: '{topic}' ---")
    
    # 1. Fetch and Combine Data
    arxiv_df = fetch_arxiv_data(topic, max_results_per_source)
    patents_df = fetch_patent_data(topic, max_results_per_source)
    combined_df = pd.concat([arxiv_df, patents_df], ignore_index=True)
    
    # 2. NEW: Pre-filter for high-quality documents before analysis
    MIN_SUMMARY_LENGTH = 150 # Require at least 150 characters for a summary to be useful
    original_count = len(combined_df)
    combined_df = combined_df[combined_df['summary'].str.len() >= MIN_SUMMARY_LENGTH]
    print(f"Filtered {original_count} documents down to {len(combined_df)} high-quality candidates for analysis.")

    if combined_df.empty:
        print("No documents with sufficient summary length found. Exiting pipeline.")
        return
        
    # 3. Process documents concurrently with smarter rate limiting
    all_insights = []
    # Reduced max_workers to a safer number for the free tier
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results_iterator = executor.map(analyze_document, combined_df.iterrows())
        all_insights = list(tqdm(results_iterator, total=len(combined_df), desc="Analyzing High-Quality Documents"))

    # 4. Save the enriched data
    if all_insights:
        processed_df = pd.DataFrame(all_insights)
        processed_df = processed_df[processed_df['strategic_summary'] != 'Analysis failed']
        if not processed_df.empty:
            save_to_db(processed_df)
    
    print("--- AETOS Pipeline finished successfully ---")

if __name__ == "__main__":
    topic_of_interest = "hypersonic missile defense"
    run_pipeline(topic=topic_of_interest)