import requests
import os

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")


def get_embedding(text: str, model: str = "all-minilm") -> list:
    response = requests.post(
        f"{OLLAMA_BASE}/api/embed", json={"model": model, "input": text}
    )
    response.raise_for_status()
    if len(response.json()["embeddings"]) != 0:
        return response.json()["embeddings"][0]
    else:
        return []
