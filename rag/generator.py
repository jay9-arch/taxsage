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

    prompt = f"""You are a tax assistant. Your ONLY job is to explain eligibility
and rules using the context below, in 2-4 sentences, naturally mentioning the
relevant section number(s). Do not mention tax amounts, calculations, liability,
or the word "final" at all \u2014 end your answer as soon as you've explained the rule
itself, with no concluding remark about what else is needed.

Context:
{context_block}

Question: {query}

Answer:"""

    answer_text = _call_groq(prompt)
    return {
        "answer": answer_text,
        "sources": [{"citation": r["citation"], "score": r["score"]} for r in retrieved],
    }
