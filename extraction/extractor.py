import json
import time
from groq import Groq
from google.colab import userdata

_client = None
MODEL_NAME = "openai/gpt-oss-20b"

def _get_client():
    global _client
    if _client is None:
        api_key = userdata.get('GROQ_API_KEY')
        _client = Groq(api_key=api_key)
    return _client

def _call_groq(prompt, max_attempts=4, base_wait=5):
    client = _get_client()
    last_error = None
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                timeout=20,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower() or "quota" in err_str.lower():
                print(f"Groq quota/rate limit hit: {e}")
                raise
            if "404" in err_str or "model_not_found" in err_str.lower():
                print(f"Groq model not found: {e}")
                raise
            wait = base_wait * (attempt + 1)
            print(f"Groq call failed (attempt {attempt+1}/{max_attempts}): {type(e).__name__}. Waiting {wait}s...")
            time.sleep(wait)
    raise last_error

SCHEMA_PROMPT = """Extract the following financial information from the user's message
and return ONLY a valid JSON object, with no other text, no markdown formatting, and no
explanation. Use these exact keys:

- "gross_income": annual gross income in rupees (integer, 0 if not mentioned)
- "section_80C": amount invested under Section 80C / PPF / ELSS / life insurance / EPF (integer, 0 if not mentioned)
- "section_80D": amount paid for medical/health insurance premium (integer, 0 if not mentioned)
- "hra_exemption": annual rent paid that could qualify for HRA exemption (integer, 0 if not mentioned)

Convert phrases like "12 lakhs" to 1200000, "1.5 lakh" to 150000, etc.

IMPORTANT: Section 80C has a maximum limit of Rs. 150000 per year, and Section 80D
has a maximum limit of Rs. 25000 per year. If the user says something like "the full
amount", "max it out", "maximum", or "fully invest" in relation to one of these
sections WITHOUT giving a specific number, use that section's maximum limit as the
value (150000 for 80C, 25000 for 80D).

User message: "{message}"

JSON:"""

def extract_profile(message):
    prompt = SCHEMA_PROMPT.format(message=message)
    raw_text = _call_groq(prompt).strip()
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
