import os
import time
import pandas as pd
from celery import Celery
from ingest import fetch_arxiv_data
from ingest_patents import fetch_patent_data
from database import save_to_db
from intelligence import get_gemini_analysis

# Keep Celery for potential async use, but API now calls sync
celery_app = Celery('aetos_tasks', broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"), backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"))

@celery_app.task(name='worker.run_analysis_pipeline_task')
def run_analysis_pipeline_task(topic: str, num_documents: int = 20):  # Increased default
    print(f"--- [Worker] Starting AETOS Batch Intelligence Run for topic: '{topic}' ---")
    max_per_source = max(1, num_documents // 2)

    arxiv_df = fetch_arxiv_data(topic, max_results=max_per_source)
    patents_df = fetch_patent_data(topic, max_results=max_per_source)
    combined_df = pd.concat([arxiv_df, patents_df], ignore_index=True, sort=False)

    # Parse published dates for sorting/filtering
    combined_df['published'] = pd.to_datetime(combined_df['published'], errors='coerce')

    MIN_SUMMARY_LENGTH = 150
    original_count = len(combined_df)
    combined_df.dropna(subset=['summary'], inplace=True)
    combined_df = combined_df[combined_df['summary'].str.len() >= MIN_SUMMARY_LENGTH]
    print(f"Filtered {original_count} docs to {len(combined_df)} high-quality candidates.")

    if combined_df.empty:
        return "Analysis complete. No high-quality documents found."

    all_insights = []
    print("Starting throttled, sequential analysis...")
    for idx, (_, row) in enumerate(combined_df.iterrows(), start=1):
        title_preview = (row.get('title') or '')[:60]
        print(f"Analyzing doc {idx}/{len(combined_df)}: {title_preview}...")
        
        # Skip very short summaries
        if len(row['summary'].split()) < 25:
            print(f"Skipping doc {idx}: Summary too short.")
            continue
            
        insights = get_gemini_analysis(row['summary'])
        
        if isinstance(insights, dict) and insights.get("TRL", 0) != 0:
            merged = row.to_dict()
            merged.update(insights)
            all_insights.append(merged)
        else:
            print(f"Warning: Analysis failed or was skipped for doc {idx}.")
        
        time.sleep(4.1)  # Rate limit

    if all_insights:
        processed_df = pd.DataFrame(all_insights)
        if not processed_df.empty:
            try:
                save_to_db(processed_df)
                return f"Analysis complete. Saved {len(processed_df)} documents."
            except Exception as e:
                return f"Analysis complete. Failed to save to DB: {e}"
    
    return "Analysis complete. No new documents were saved."