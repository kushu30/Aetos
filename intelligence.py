# intelligence.py
from dotenv import load_dotenv
load_dotenv()

import os
import google.generativeai as genai
import json
import time
from google.api_core.exceptions import ResourceExhausted

def get_gemini_analysis(text: str, max_retries: int = 3) -> dict:
    # 1. NEW: Input validation before making an API call
    if not text or len(text.split()) < 20: # Check for empty text or less than 20 words
        return { "strategic_summary": "Not analyzed: Summary too short.", "technologies": [], "key_relationships": [] }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return {}

    try:
        genai.configure(api_key=api_key)
        # 2. NEW: Added safety settings for more reliable responses
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        model = genai.GenerativeModel(
            'gemini-2.5-flash-lite-preview-09-2025',
            safety_settings=safety_settings
        )
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return {}

    prompt = f"""
    Analyze the following research paper abstract from the perspective of a defense technology analyst. Your primary goal is to identify the core technologies, their relationships, and the strategic importance of the work.

    Abstract: "{text}"

    Based on the abstract, provide your analysis strictly in the following JSON format. Ensure your entire output is a single, valid JSON object and nothing else.
    {{
      "strategic_summary": "A concise, one-sentence summary of why this research is important and its potential application.",
      "technologies": ["List", "of", "key", "technologies", "or", "methods"],
      "key_relationships": [
        {{
          "subject": "Technology A",
          "relationship": "is used to improve/enable/detect",
          "object": "Technology B"
        }}
      ]
    }}
    """

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            json_response = response.text.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(json_response)
        except ResourceExhausted:
            print(f"Rate limit exceeded (Attempt {attempt + 1}/{max_retries}). Waiting...")
            time.sleep(60)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from Gemini response on attempt {attempt + 1}")
            time.sleep(5) # Short wait before retrying a malformed response
        except Exception as e:
            print(f"An unexpected error occurred during Gemini API call: {e}")
            break

    return { "strategic_summary": "Analysis failed after multiple retries", "technologies": [], "key_relationships": [] }