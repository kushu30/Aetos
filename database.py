# database.py
import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

def save_to_db(df: pd.DataFrame, db_name: str = "aetos_db", collection_name: str = "documents"):
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("MONGO_URI not found in environment variables.")

    print("Connecting to MongoDB...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    records = df.to_dict('records')
    
    print(f"Upserting {len(records)} documents into '{db_name}.{collection_name}'...")
    
    upsert_count = 0
    for record in records:
        result = collection.update_one(
            {'id': record['id']}, 
            {'$set': record}, 
            upsert=True
        )
        if result.upserted_id:
            upsert_count += 1
            
    print(f"Database operation complete. Inserted {upsert_count} new documents.")
    client.close()

def save_analytics_to_db(data: dict, db_name: str = "aetos_db", collection_name: str = "analytics"):
    """Saves analysis data, like S-curves, to a dedicated collection."""
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("MONGO_URI not found in environment variables.")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    topic_id = data.get("topic")
    if not topic_id:
        print("Analytics data must contain a 'topic' field.")
        return

    print(f"Upserting analytics for topic '{topic_id}'...")
    collection.update_one(
        {'_id': topic_id},
        {'$set': data},
        upsert=True
    )
    
    print("Analytics data saved successfully.")
    client.close()