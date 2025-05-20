import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)

QDRANT_URL = os.getenv("QDRANT_HOST", "http://localhost:6333")
client = QdrantClient(url=QDRANT_URL)


def init_collection(name: str):
    if not client.collection_exists(name):
        client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def store_vector(collection: str, text: str, metadata: dict, vector: list):
    point = PointStruct(
        id=str(uuid.uuid4()), vector=vector, payload=metadata | {"text": text}
    )
    client.upsert(collection, points=[point])


def delete_vector(collection: str, field: str, value: str):
    filter = Filter(must=[FieldCondition(key=field, match=MatchValue(value=value))])
    client.delete(
        collection_name=collection, points_selector=FilterSelector(filter=filter)
    )
