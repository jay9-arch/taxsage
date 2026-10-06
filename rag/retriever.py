from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from data.tax_knowledge import TAX_CHUNKS

_model = None
_index = None
_chunks = TAX_CHUNKS

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def build_index():
    global _index
    model = _get_model()
    texts = [c["text"] for c in _chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    dim = embeddings.shape[1]
    _index = faiss.IndexFlatIP(dim)
    _index.add(embeddings)
    return _index

def retrieve(query, top_k=3):
    global _index
    if _index is None:
        build_index()
    model = _get_model()
    q_embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, indices = _index.search(q_embedding, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        chunk = _chunks[idx]
        results.append({**chunk, "score": float(score)})
    return results
