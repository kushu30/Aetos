# intelligence.py
from dotenv import load_dotenv
load_dotenv()

import os, json, time, re, google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

generation_config = genai.types.GenerationConfig(
    response_mime_type="application/json",
)

# ... (keep existing get_gemini_analysis function) ...
def get_gemini_analysis(text: str, max_retries: int = 3) -> dict:
    if not text or len(text.split()) < 25:
        return {"TRL": 0, "strategic_summary": "Not analyzed: Abstract too short."}

    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config=generation_config)
    
    prompt = f"""
    As a senior defense technology analyst, analyze the following abstract. Provide a structured intelligence report in JSON format.

    Abstract: "{text}"

    Your entire output must be a single, valid JSON object.
    {{
      "TRL": <integer_from_1_to_9>,
      "TRL_justification": "A brief explanation for the TRL score.",
      "strategic_summary": "A concise, one-sentence summary of why this research is important.",
      "technologies": ["List", "of", "key", "technologies"],
      "key_relationships": [
        {{"subject": "Technology A", "relationship": "is used to improve", "object": "Technology B"}}
      ],
      "country": "The country of origin of the research, if mentioned.",
      "provider_company": "The company or institution providing the technology, if mentioned.",
      "funding_details": "Any details about funding for this research, if mentioned."
    }}
    """

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Received empty response text from Gemini.")

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

def get_gemini_analysis(text: str, max_retries: int = 3) -> dict:
    if not text or len(text.split()) < 25:
        return {"TRL": 0, "strategic_summary": "Not analyzed: Abstract too short."}

    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config=generation_config)
    
    prompt = f"""
    As a senior defense technology analyst, analyze the following abstract. Provide a structured intelligence report in JSON format.

    Abstract: "{text}"

    Your entire output must be a single, valid JSON object.
    {{
      "TRL": <integer_from_1_to_9>,
      "TRL_justification": "A brief explanation for the TRL score.",
      "strategic_summary": "A concise, one-sentence summary of why this research is important.",
      "technologies": ["List", "of", "key", "technologies"],
      "key_relationships": [
        {{"subject": "Technology A", "relationship": "is used to improve", "object": "Technology B"}}
      ],
      "country": "The country of origin of the research, if mentioned.",
      "provider_company": "The company or institution providing the technology, if mentioned.",
      "funding_details": "Any details about funding for this research, if mentioned."
    }}
    """

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Received empty response text from Gemini.")

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


def get_gemini_topic_synthesis(summaries: list, topic: str) -> dict:
    """Synthesizes summaries and generates mock analytics data."""
    if not summaries:
        return {"error": "No content provided for synthesis."}
    
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config=generation_config)
    
    combined_text = "\n\n---\n\n".join(summaries)
    
    prompt = f"""
    You are a senior technology intelligence analyst. Based on the provided abstracts for the topic "{topic}", generate a comprehensive intelligence report in a single, valid JSON object.

    Abstracts:
    ---
    {combined_text}
    ---
    
    Your report must contain:
    - `overall_summary`: A high-level summary of the technology area.
    - `emerging_signals`: A list of 2-3 early but potentially significant trends.
    - `key_players`: A list of the most frequently mentioned companies, countries, or institutions.
    - `mock_s_curve`: An array of 7 objects, each with a 'year' and 'cumulative_count', representing a plausible S-curve for this technology's adoption.
    - `mock_trl_progression`: An object with two keys: 'history' (an array of 5 objects with 'year' and 'avg_trl') and 'forecast' (an array of 3 objects with 'year' and 'avg_trl'). This should represent a plausible TRL progression and forecast.

    Example for s_curve and trl_progression:
    "mock_s_curve": [
      {{"year": 2018, "cumulative_count": 5}}, {{"year": 2019, "cumulative_count": 15}}, ...
    ],
    "mock_trl_progression": {{
      "history": [{{"year": 2020, "avg_trl": 2.5}}, {{"year": 2021, "avg_trl": 3.1}}, ...],
      "forecast": [{{"year": 2025, "avg_trl": 5.3}}, {{"year": 2026, "avg_trl": 5.8}}, ...]
    }}

    JSON Output Format:
    {{
      "overall_summary": "...",
      "emerging_signals": ["...", "..."],
      "key_players": ["...", "..."],
      "mock_s_curve": [{{...}}],
      "mock_trl_progression": {{ "history": [{{...}}], "forecast": [{{...}}] }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        if not response.text:
            raise ValueError("Received empty response text from Gemini for synthesis.")
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            raise ValueError("No JSON object found in Gemini response for synthesis.")
            
    except Exception as e:
        print(f"An error occurred during Gemini synthesis: {e}")
        return {"error": f"Failed to generate synthesis. Reason: {str(e)}"}