import json
from google import genai
from google.colab import userdata

_client = None
MODEL_NAME = "gemini-3.5-flash"

def _get_client():
    global _client
    if _client is None:
        api_key = userdata.get('GEMINI_API_KEY')
        _client = genai.Client(api_key=api_key)
    return _client

SCHEMA_PROMPT = """Extract the following financial information from the user's message
and return ONLY a valid JSON object, with no other text, no markdown formatting, and no
explanation. Use these exact keys:

- "gross_income": annual gross income in rupees (integer, 0 if not mentioned)
- "section_80C": amount invested under Section 80C / PPF / ELSS / life insurance / EPF (integer, 0 if not mentioned)
- "section_80D": amount paid for medical/health insurance premium (integer, 0 if not mentioned)
- "hra_exemption": annual rent paid that could qualify for HRA exemption (integer, 0 if not mentioned)

Convert phrases like "12 lakhs" to 1200000, "1.5 lakh" to 150000, etc.

User message: "{message}"

JSON:"""

def extract_profile(message):
    client = _get_client()
    prompt = SCHEMA_PROMPT.format(message=message)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw_output": raw_text}

    for key in ["gross_income", "section_80C", "section_80D", "hra_exemption"]:
        if key not in parsed or not isinstance(parsed[key], (int, float)) or parsed[key] < 0:
            return {"error": f"Invalid or missing field: {key}", "raw_output": raw_text}

    return parsed
