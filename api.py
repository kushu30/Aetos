# api.py
import json
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from ingest import fetch_arxiv_data
from ingest_patents import fetch_patent_data
import pandas as pd
from intelligence import get_gemini_briefing_for_topic
from worker import run_analysis_pipeline_task

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
load_dotenv()

@app.route("/api/analyze/<topic>", methods=['GET'])
def analyze_topic_live(topic):
    print(f"\n--- [Fast Path] Received request for topic: '{topic}' ---")
    try:
        # 1. Fetch data
        print("Step 1: Fetching documents from arXiv and Patents...")
        arxiv_df = fetch_arxiv_data(topic, max_results=7)
        patents_df = fetch_patent_data(topic, max_results=7)
        
        if arxiv_df.empty and patents_df.empty:
            print(">>> STATUS: FAILED. Could not fetch from any data source.")
            return jsonify({"error": "Failed to fetch data from all primary sources. The services may be temporarily unavailable."}), 503

        combined_df = pd.concat([arxiv_df, patents_df], ignore_index=True)
        print(f"Step 2: Found {len(combined_df)} total documents. Filtering for quality...")

        # 2. Filter for quality
        combined_df.dropna(subset=['summary'], inplace=True) # Ensure summary exists
        combined_df = combined_df[combined_df['summary'].str.len() >= 200].head(7) # Stricter filter
        
        if combined_df.empty:
            print(">>> STATUS: FAILED. No documents met the quality criteria for a live briefing.")
            return jsonify({"error": "Could not find enough high-quality documents for a live analysis."}), 404
        
        print(f"Step 3: Found {len(combined_df)} high-quality documents. Preparing briefing...")
        abstracts = combined_df['summary'].tolist()
        
        # 3. Get the Gemini Briefing
        briefing = get_gemini_briefing_for_topic(abstracts)
        
        if not briefing or "error" in briefing:
            print(f">>> STATUS: FAILED. Gemini analysis returned an error: {briefing.get('error', 'Unknown')}")
            return jsonify(briefing), 500

        print("Step 4: Briefing generated successfully. Triggering background deep-dive...")
        # 4. Trigger background analysis and return success
        run_analysis_pipeline_task.delay(topic, num_documents=100) # Deeper analysis
        
        print("--- [Fast Path] Request successful. Sending briefing to user. ---")
        return jsonify(briefing)

    except Exception as e:
        print(f"!!! An unexpected error occurred in the fast path: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)