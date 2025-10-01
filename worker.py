# worker.py
import pandas as pd
import concurrent.futures
from celery import Celery
from ingest import fetch_arxiv_data
from ingest_patents import fetch_patent_data
from database import save_to_db
from intelligence import get_gemini_analysis

celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery_app.task(name='worker.run_analysis_pipeline_task')
def run_analysis_pipeline_task(topic: str, num_documents: int = 50):
    print(f"--- [Celery Worker] Starting AETOS Batch Intelligence Run for topic: '{topic}' ---")
    
    max_per_source = num_documents // 2
    
    arxiv_df = fetch_arxiv_data(topic, max_results=max_per_source)
    patents_df = fetch_patent_data(topic, max_results=max_per_source)
    combined_df = pd.concat([arxiv_df, patents_df], ignore_index=True)
    
    MIN_SUMMARY_LENGTH = 150
    original_count = len(combined_df)
    combined_df = combined_df[combined_df['summary'].str.len() >= MIN_SUMMARY_LENGTH]
    print(f"Filtered {original_count} docs down to {len(combined_df)} high-quality candidates.")

    if combined_df.empty:
        return f"Analysis for '{topic}' complete. No high-quality documents found."
        
    def analyze_document(row_tuple):
        insights = get_gemini_analysis(row_tuple[1]['summary'])
        # --- THIS IS THE FIX ---
        if insights and isinstance(insights, dict):
            return {**row_tuple[1].to_dict(), **insights}
        else:
            print(f"Warning: Gemini analysis returned an invalid result for a document. Skipping.")
            return None # This will be filtered out later
    
    all_insights = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results_iterator = executor.map(analyze_document, combined_df.iterrows())
        all_insights = list(results_iterator)

    # Filter out any results that failed the safety check
    all_insights = [item for item in all_insights if item is not None]

    if all_insights:
        processed_df = pd.DataFrame(all_insights)
        processed_df = processed_df[processed_df['TRL'] != 0]
        if not processed_df.empty:
            print(f"Saving {len(processed_df)} documents to the database.")
            save_to_db(processed_df)
            return f"Analysis for '{topic}' complete. Saved {len(processed_df)} documents."
    
    return f"Analysis for '{topic}' complete. No new documents were saved."