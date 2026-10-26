import json
import math
import os
from datetime import datetime
from json import JSONDecodeError

import requests

from config import KEYS, BASE_DIR

OPENROUTER_EMBEDDING_URL = "https://openrouter.ai/api/v1/embeddings"
OPENROUTER_EMBEDDING_MODEL = "sentence-transformers/all-minilm-l6-v2"

PROMPT_SIM_THRESHOLD = 0.65
PROMPT_SIM_NEAR_DUP_THRESHOLD = 0.9
PROMPT_SIM_MIN_CHARS = 40
PROMPT_SIM_TOP_K = 5
PROMPT_EMBEDDING_INDEX_PATH = str(BASE_DIR / "data" / "mainland" / "prompt_embeddings.json")


def _ensure_index_dir():
    os.makedirs(os.path.dirname(PROMPT_EMBEDDING_INDEX_PATH), exist_ok=True)


def _normalize_header(value):
    return str(value).strip().lower()


def _normalize_vector(vector):
    norm = math.sqrt(sum((x * x) for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    return float(sum((a * b) for a, b in zip(vec_a, vec_b)))


def embed_prompt_openrouter(prompt):
    # OPENAI_API_KEY is the legacy name for an OpenRouter embedding credential.
    key = next((str(KEYS.get(name) or '').strip() for name in (
        'OPENROUTER_EMBEDDING_API_KEY', 'OPENROUTER_LLAMA_API_KEY',
        'OPENROUTER_DEEPSEEK_API_KEY', 'OPENAI_API_KEY',
    ) if str(KEYS.get(name) or '').strip()), '')
    if not key:
        raise RuntimeError('No OpenRouter key is configured for similarity checks.')
    try:
        response = requests.post(
            OPENROUTER_EMBEDDING_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={"model": OPENROUTER_EMBEDDING_MODEL, "input": prompt},
            timeout=30,
        )
    except requests.RequestException:
        raise RuntimeError('The similarity service could not be reached. Please try again.') from None
    if not response.ok:
        if response.status_code in (401, 402, 403):
            raise RuntimeError('OpenRouter embedding access was denied. Check the key permissions and available credits.')
        raise RuntimeError(f'The similarity service returned HTTP {response.status_code}. Please try again.')
    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError('The similarity service returned an invalid response.') from None

    data = payload.get("data", []) if isinstance(payload, dict) else []
    if not data or not isinstance(data, list) or not isinstance(data[0], dict) or "embedding" not in data[0]:
        raise ValueError('The similarity service returned no embedding.')

    embedding = data[0]["embedding"]
    if not isinstance(embedding, list) or not embedding:
        raise ValueError("OpenRouter returned an empty embedding.")

    try:
        vector = [float(x) for x in embedding]
    except (TypeError, ValueError):
        raise ValueError('The similarity service returned an invalid embedding.') from None
    if not all(math.isfinite(x) for x in vector) or not any(vector):
        raise ValueError('The similarity service returned an invalid embedding.')
    return _normalize_vector(vector)


def load_prompt_index():
    _ensure_index_dir()
    if not os.path.exists(PROMPT_EMBEDDING_INDEX_PATH):
        return {"version": 1, "items": {}}

    try:
        with open(PROMPT_EMBEDDING_INDEX_PATH, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if not raw:
                return {"version": 1, "items": {}}
            data = json.loads(raw)
    except (OSError, JSONDecodeError):
        # Recover gracefully if file is truncated/empty/invalid.
        return {"version": 1, "items": {}}

    if not isinstance(data, dict):
        return {"version": 1, "items": {}}

    version = data.get("version", 1)
    items = data.get("items", {})
    if not isinstance(items, dict):
        items = {}

    return {"version": version, "items": items}


def save_prompt_index(index_data):
    _ensure_index_dir()
    tmp_path = f"{PROMPT_EMBEDDING_INDEX_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False)
    os.replace(tmp_path, PROMPT_EMBEDDING_INDEX_PATH)


def upsert_prompt_embedding(annotation_id, state, base_prompt, embedding):
    if not annotation_id:
        raise ValueError("annotation_id is required for embedding upsert")

    index_data = load_prompt_index()
    index_data["items"][annotation_id] = {
        "annotation_id": annotation_id,
        "state": state or "",
        "base_prompt": base_prompt or "",
        "embedding": embedding,
        "updated_at": datetime.utcnow().isoformat(),
    }
    save_prompt_index(index_data)


def remove_prompt_embedding(annotation_id):
    if not annotation_id:
        return

    index_data = load_prompt_index()
    if annotation_id in index_data["items"]:
        del index_data["items"][annotation_id]
        save_prompt_index(index_data)


def upsert_prompt_embedding_for_record(record):
    annotation_id = record.get("id")
    state = record.get("state", "")
    base_prompt = record.get("prompts", {}).get("base", "")
    if not base_prompt or _normalize_header(base_prompt) == "":
        return

    cached = load_prompt_index().get('items', {}).get(annotation_id, {})
    if (cached.get('base_prompt') == base_prompt and cached.get('state') == state
            and isinstance(cached.get('embedding'), list) and cached['embedding']):
        return

    embedding = embed_prompt_openrouter(base_prompt)
    upsert_prompt_embedding(annotation_id, state, base_prompt, embedding)


def find_similar_for_state(prompt, state, threshold=PROMPT_SIM_THRESHOLD, top_k=PROMPT_SIM_TOP_K, exclude_annotation_id=None):
    index_data = load_prompt_index()
    items = index_data.get("items", {})
    matches = []

    candidates = {
        annotation_id: item for annotation_id, item in items.items()
        if annotation_id != exclude_annotation_id
        and _normalize_header(item.get('state', '')) == _normalize_header(state)
        and item.get('base_prompt')
        and isinstance(item.get('embedding'), list) and item['embedding']
    }
    if not candidates:
        return []
    query_embedding = embed_prompt_openrouter(prompt)

    for annotation_id, item in candidates.items():
        if exclude_annotation_id and annotation_id == exclude_annotation_id:
            continue

        base_prompt = item.get("base_prompt", "")
        vector = item.get("embedding")
        if not base_prompt or not isinstance(vector, list) or not vector:
            continue

        score = cosine_similarity(query_embedding, vector)
        if score >= threshold:
            matches.append({
                "annotation_id": annotation_id,
                "prompt": base_prompt,
                "similarity": round(float(score), 4),
            })

    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches[:top_k]
