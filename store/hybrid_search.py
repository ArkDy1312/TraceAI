from store.embedder import get_embedding
from store.llm_chat import intent_detector
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

import os

QDRANT_URL = os.getenv("QDRANT_HOST", "http://localhost:6333")
client = QdrantClient(url=QDRANT_URL)


def hybrid_search(query: str, workspace_id: str, feature_id: str, top_k=5):
    vector = get_embedding(query)
    intents = intent_detector(query)
    intent_list = [i.strip() for i in intents.split(",")]

    payload_filter = None
    if intent_list:
        # Filter to return only documents that have this metadata key
        payload_filter = Filter(
            must=[FieldCondition(key="feature_id", match=MatchValue(value=feature_id))],
            should=[
                FieldCondition(key=intent, is_empty=False) for intent in intent_list
            ],
        )

    results = []

    collection = workspace_id
    try:
        v_hits = client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
            query_filter=payload_filter,
        )
        for hit in v_hits:
            results.append({"score": hit.score, "payload": hit.payload})
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

    return sorted(results, key=lambda x: -x["score"])[:top_k], intent_list
