import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util
import json
import pandas as pd
from worker import run_analysis_pipeline_task
# --- NEW IMPORTS ---
from intelligence import get_gemini_topic_synthesis
from analytics import calculate_s_curve, find_technology_convergence, calculate_trl_progression

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client.get_database("aetos_db")

    def get_docs_for_topic(topic):
        """Helper function to fetch documents for a topic."""
        query = {
            "$or": [
                {"title": {"$regex": topic, "$options": "i"}},
                {"technologies": {"$regex": topic, "$options": "i"}}
            ]
        }
        return list(db.documents.find(query))

    @app.route("/api/documents/<topic>", methods=['GET'])
    def get_documents(topic):
        print(f"API: Received request for documents on topic: '{topic}'")
        documents = get_docs_for_topic(topic)
        print(f"API: Found {len(documents)} matching documents.")
        return jsonify(json.loads(json_util.dumps(documents)))

    @app.route("/api/analyze/<topic>", methods=['POST'])
    def analyze_topic(topic):
        data = request.get_json()
        num_documents = data.get('num_documents', 50)
        
        print(f"API: Received analysis request for '{topic}' for {num_documents} documents. Running synchronously.")
        try:
            result = run_analysis_pipeline_task(topic, num_documents=num_documents)
            return jsonify({"status": "Analysis complete", "result": result}), 200
        except Exception as e:
            print(f"API: Error during analysis: {e}")
            return jsonify({"status": "Analysis failed", "error": str(e)}), 500

    # --- NEW ANALYTICS ENDPOINTS ---

    @app.route("/api/analytics/synthesis/<topic>", methods=['GET'])
    def get_synthesis_and_charts(topic):
        documents = get_docs_for_topic(topic)
        if not documents:
            return jsonify({"error": "No documents found for synthesis."}), 404
        
        # We need summaries for the prompt, but the function will return all analytics data
        summaries = [doc['summary'] for doc in documents if 'summary' in doc]
        
        # Pass the topic to the synthesis function
        synthesis_data = get_gemini_topic_synthesis(summaries[:20], topic)
        
        # For convergence, we still use the real data
        df = pd.DataFrame(json.loads(json_util.dumps(documents)))
        convergence_data = find_technology_convergence(df)
        
        # Combine the results
        synthesis_data['convergence'] = convergence_data
        
        return jsonify(synthesis_data)

    return app

    # @app.route("/api/analytics/scurve/<topic>", methods=['GET'])
    # def get_scurve(topic):
    #     documents = get_docs_for_topic(topic)
    #     if not documents:
    #         return jsonify([]), 404
    #     df = pd.DataFrame(json.loads(json_util.dumps(documents)))
    #     s_curve_data = calculate_s_curve(df)
    #     return jsonify(s_curve_data)

    # @app.route("/api/analytics/convergence/<topic>", methods=['GET'])
    # def get_convergence(topic):
    #     documents = get_docs_for_topic(topic)
    #     if not documents:
    #         return jsonify([]), 404
    #     df = pd.DataFrame(json.loads(json_util.dumps(documents)))
    #     convergence_data = find_technology_convergence(df)
    #     return jsonify(convergence_data)

    # @app.route("/api/analytics/trl_progression/<topic>", methods=['GET'])
    # def get_trl_progression(topic):
    #     documents = get_docs_for_topic(topic)
    #     if not documents:
    #         return jsonify({"history": [], "forecast": []}), 404
    #     df = pd.DataFrame(json.loads(json_util.dumps(documents)))
    #     trl_data = calculate_trl_progression(df)
    #     return jsonify(trl_data)

    # return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=int(os.getenv("API_PORT", 5000)))