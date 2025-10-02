# intelligence.py
from dotenv import load_dotenv
load_dotenv()

import os, json, time, re, google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

generation_config = genai.types.GenerationConfig(
    response_mime_type="application/json",
)

def get_gemini_analysis(text: str, max_retries: int = 3) -> dict:
    if not text or len(text.split()) < 25:
        return {"TRL": 0, "strategic_summary": "Not analyzed: Abstract too short."}

    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config=generation_config)
    
    prompt = f"""
    As a senior defense technology analyst, analyze the following abstract. Provide a structured intelligence report in JSON format with TRL estimation, a strategic summary, key technologies, and their relationships.

    Abstract: "{text}"

    Your entire output must be a single, valid JSON object.
    {{
      "TRL": <integer_from_1_to_9>,
      "TRL_justification": "A brief explanation for the TRL score.",
      "strategic_summary": "A concise, one-sentence summary of why this research is important.",
      "technologies": ["List", "of", "key", "technologies"],
      "key_relationships": [
        {{"subject": "Technology A", "relationship": "is used to improve", "object": "Technology B"}}
      ]
    }}
    """

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            # Defensive check: ensure response text is not empty
            if not response.text:
                raise ValueError("Received empty response text from Gemini.")

            # Defensive parsing: use regex to find the JSON object
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError("No JSON object found in Gemini response.")

        except (ResourceExhausted, Exception) as e:
            print(f"Error in get_gemini_analysis (Attempt {attempt + 1}/{max_retries}): {e}. Waiting...")
            if attempt < max_retries - 1:
                time.sleep(60)
            
    return {"TRL": 0, "strategic_summary": "Analysis failed after all retries."}


def get_gemini_briefing_for_topic(abstracts: list) -> dict:
    if not abstracts: 
        return {"error": "No content provided for analysis."}
    
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config=generation_config)
    combined_text = "\n\n---\n\n".join(abstracts)
    
    prompt = f"""
    You are a senior technology intelligence analyst for a national defense organization (DRDO). Synthesize the following collection of abstracts into a single, high-impact executive briefing in a strict JSON format.

    Abstracts:
    ---
    {combined_text}
    ---
    
    If you cannot perform the analysis, you MUST return a JSON object with a single "error" key. Otherwise, your report must contain:
    `strategic_summary`, `aggregate_TRL`, `TRL_justification`, `key_technologies`, `emerging_convergences`.

    JSON Output Format:
    {{
      "strategic_summary": "...",
      "aggregate_TRL": <integer>,
      "TRL_justification": "...",
      "key_technologies": ["..."],
      "emerging_convergences": [
        {{"subject": "Technology A", "relationship": "is converging with", "object": "Technology B"}}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        if not response.text:
            raise ValueError("Received empty response text from Gemini for briefing.")
        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred during Gemini briefing generation: {e}")
        return {"error": f"Failed to generate intelligence briefing. Reason: {str(e)}"}