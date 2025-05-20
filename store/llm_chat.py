import requests
import os
from config.prompt_templates import INTENT_PROMPT, EXISTS_PROMPT, NOT_EXISTS_PROMPT

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model = "gemma3:1b" #or tinyllama

def intent_detector(question: str) -> str:
    intent_prompt_template = INTENT_PROMPT

    intent_prompt = intent_prompt_template.format(question=question)

    intent_response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={"model": model, "prompt": intent_prompt, "stream": False}
    )
    intent_response.raise_for_status()
    return intent_response.json()["response"].strip()

def llm_call(context: str, question: str) -> str:
    if len(context) == 0:
        prompt_template = NOT_EXISTS_PROMPT
        prompt = prompt_template.format(question=question)
    else:
        prompt_template = EXISTS_PROMPT
        prompt = prompt_template.format(context=context, question=question)

    print(f"Prompt: {prompt}", flush=True)

    response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    return response.json()["response"].strip()
