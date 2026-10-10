from groq import Groq
from google.colab import userdata
from rag.retriever import retrieve
import time

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

def answer_question(query, top_k=3):
    retrieved = retrieve(query, top_k=top_k)
    context_block = "\n\n".join(f"[{r['citation']}]: {r['text']}" for r in retrieved)

    prompt = f"""You are one part of a two-part tax assistant system. The user's
question below may contain TWO kinds of requests mixed together: (1) a question
about rules/eligibility, and (2) a request for an exact tax amount or calculation.
A separate, different part of the system already handles part (2) and shows the
user that number elsewhere on the screen. Your job covers ONLY part (1).

Silently ignore any part of the question asking for an amount, calculation, or
"tell me my tax" \u2014 treat the question as if that part was never asked. Answer
using the context below, in 2-4 sentences, naturally mentioning the relevant
section number(s).

Example of correct behavior:
Question: "Explain HRA and tell me my tax if I claim 2 lakh, income 10 lakh."
Correct answer: "HRA exemption under Section 10(13A) allows salaried individuals
to reduce taxable income based on actual rent paid, subject to specific
conditions tied to salary and city of residence. It is only available under the
Old Tax Regime, not the New Regime."
(Notice: no mention of tax amount, no apology, no "I can't calculate" statement
 \u2014 the amount part of the question is simply not addressed at all.)

Context:
{context_block}

Question: {query}

Answer:"""

    answer_text = _call_groq(prompt)
    return {
        "answer": answer_text,
        "sources": [{"citation": r["citation"], "score": r["score"]} for r in retrieved],
    }
