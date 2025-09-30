# api.py
import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client.aetos_db

    @app.route("/")
    def index():
        return json_util.dumps({"status": "AETOS API is running successfully"})

    @app.route("/api/documents", methods=['GET'])
    def get_documents():
        # This is now the single source of truth for our dashboard
        documents = list(db.documents.find().sort("published", -1).limit(50))
        return json_util.dumps(documents)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)