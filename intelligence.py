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

# --- NEW FUNCTION ---
def get_gemini_topic_synthesis(summaries: list) -> dict:
    """Synthesizes multiple summaries to identify high-level signals."""
    if not summaries: 
        return {"error": "No content provided for synthesis."}
    
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config=generation_config)
    
    combined_text = "\n\n---\n\n".join(summaries)
    
    prompt = f"""
    You are a senior technology intelligence analyst. Based on the following collection of document abstracts, synthesize the key insights into a single JSON object.

    Abstracts:
    ---
    {combined_text}
    ---
    
    Your report must contain:
    - `overall_summary`: A high-level summary of the technology area.
    - `emerging_signals`: A list of 2-3 early but potentially significant trends or novel concepts.
    - `key_players`: A list of the most frequently mentioned companies, countries, or institutions.

    Your entire output must be a single, valid JSON object.
    {{
      "overall_summary": "...",
      "emerging_signals": ["Signal 1...", "Signal 2..."],
      "key_players": ["Player 1", "Player 2"]
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