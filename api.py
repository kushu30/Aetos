import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util
import json  # Import the standard json library
from worker import run_analysis_pipeline_task

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client.get_database("aetos_db")

    @app.route("/api/documents/<topic>", methods=['GET'])
    def get_documents(topic):
        print(f"API: Received request for documents on topic: '{topic}'")
        query = {
            "$or": [
                {"title": {"$regex": topic, "$options": "i"}},
                {"technologies": {"$regex": topic, "$options": "i"}}
            ]
        }
        documents = list(db.documents.find(query).sort("published", -1).limit(50))
        print(f"API: Found {len(documents)} matching documents.")
        
        # --- FIX ---
        # Convert BSON to a Python list of dicts, then return as a proper JSON response
        return jsonify(json.loads(json_util.dumps(documents)))

    @app.route("/api/analyze/<topic>", methods=['POST'])
    def analyze_topic(topic):
        print(f"API: Received analysis request for '{topic}'. Running synchronously.")
        try:
            result = run_analysis_pipeline_task(topic, num_documents=5)
            return jsonify({"status": "Analysis complete", "result": result}), 200
        except Exception as e:
            print(f"API: Error during analysis: {e}")
            return jsonify({"status": "Analysis failed", "error": str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=int(os.getenv("API_PORT", 5000)))