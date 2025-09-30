# engine.py
import pandas as pd
from transformers import pipeline
from keybert import KeyBERT
from tqdm import tqdm

def process_documents(df: pd.DataFrame) -> pd.DataFrame:
    print("Initializing AI models...")
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6", framework="pt")
    ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True, framework="pt")
    kw_model = KeyBERT()
    print("Models initialized.")
    
    results = []
    print("Processing documents...")
    for summary_text in tqdm(df['summary'], total=len(df), desc="Analyzing Papers"):
        if not summary_text or not isinstance(summary_text, str):
            results.append(("No summary available", [], []))
            continue
            
        generated_summary = summarizer(summary_text[:1024], max_length=60, min_length=20, do_sample=False)[0]['summary_text']
        
        entities = ner_pipeline(summary_text)
        
        # --- THIS IS THE FIX ---
        # Convert any numpy types in entities to standard Python types
        for entity in entities:
            entity['score'] = float(entity['score'])
            
        keywords = kw_model.extract_keywords(summary_text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
        results.append((generated_summary, entities, [kw[0] for kw in keywords]))

    df[['generated_summary', 'entities', 'keywords']] = pd.DataFrame(results, index=df.index)
    
    print("Processing complete.")
    return df