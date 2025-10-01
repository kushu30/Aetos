# intelligence.py
# (Ensure all your imports like os, json, time, re, etc. are at the top)
from dotenv import load_dotenv; load_dotenv()
import os, json, time, re, google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# This config forces the model to output raw JSON. This is the key to stability.
generation_config = genai.types.GenerationConfig(
    response_mime_type="application/json",
)

def get_gemini_analysis(text: str, max_retries: int = 3) -> dict:
    if not text or len(text.split()) < 25:
        return {"TRL": 0, "strategic_summary": "Not analyzed: Abstract too short."}
    
    #... (rest of the function setup, api_key, etc.)
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-2.5-flash-lite-preview-09-2025',
        generation_config=generation_config # Apply JSON config here
    )
    prompt = f"""...""" # Your full prompt for single-document analysis

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            # With response_mime_type, the output should be clean JSON already
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in get_gemini_analysis (Attempt {attempt + 1}): {e}. Waiting...")
            time.sleep(60)
            
    return {"TRL": 0, "strategic_summary": "Analysis failed after multiple retries."}


def get_gemini_briefing_for_topic(abstracts: list) -> dict:
    if not abstracts: 
        return {"error": "No content provided for analysis."}
    
    #... (rest of the function setup, api_key, etc.)
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        'gemini-2.5-flash-lite-preview-09-2025',
        generation_config=generation_config # Apply JSON config here
    )
    combined_text = "\n\n---\n\n".join(abstracts)
    prompt = f"""...""" # Your full prompt for the briefing
    
    try:
        response = model.generate_content(prompt)
        # With response_mime_type, the output should be clean JSON already
        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred during Gemini briefing generation: {e}")
        return {"error": f"Failed to generate intelligence briefing. Reason: {str(e)}"}

# NOTE: You will need to copy your full prompts back into the `prompt = f"""..."""` sections
# of the functions above.