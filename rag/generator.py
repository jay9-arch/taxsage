from google import genai
from google.colab import userdata
from rag.retriever import retrieve

_client = None
MODEL_NAME = "gemini-3.5-flash"  # check ai.google.dev if this gets deprecated later

def _get_client():
    global _client
    if _client is None:
        api_key = userdata.get('GEMINI_API_KEY')
        _client = genai.Client(api_key=api_key)
    return _client

def answer_question(query, top_k=3):
    retrieved = retrieve(query, top_k=top_k)

    context_block = "\n\n".join(
        f"[{r['citation']}]: {r['text']}" for r in retrieved
    )

    prompt = f"""You are a tax assistant. Answer the user's question using ONLY the
information in the context below. If the context doesn't fully answer the question,
say what's missing. Keep the answer to 2-4 sentences. Mention the relevant section
number(s) naturally in your answer.

Context:
{context_block}

Question: {query}

Answer:"""

    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return {
        "answer": response.text,
        "sources": [{"citation": r["citation"], "score": r["score"]} for r in retrieved],
    }
