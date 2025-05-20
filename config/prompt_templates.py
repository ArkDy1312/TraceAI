EXISTS_PROMPT = """
You are a friendly traceability assistant. Based on the CONTEXT provided, answer the QUESTION clearly and informatively.

If the CONTEXT includes evidence (such as test names, statuses, or commit IDs/names, messages), explain whether the feature has been tested, verified, committed or implemented, and support your answer with that evidence.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

NOT_EXISTS_PROMPT = """
You are a friendly traceability assistant. Based on the QUESTION provided, write a clear sentence indicating that the intended action (e.g commit or test) mentioned in the QUESTION has not yet been completed or recorded.

QUESTION:
{question}

ANSWER:
"""

INTENT_PROMPT = """
Your task is to identify all applicable intents from a fixed list, based on the user's QUESTION.

Each intent refers to a specific kind of technical traceability information. Match the QUESTION only to the intents that are explicitly or clearly implied. Return multiple intents as a comma-separated list. If no intent applies, respond with "unknown".

Respond only with intent keywords — no extra words or explanations.

VALID INTENTS:
- commit_ID        → questions about whether a feature was committed, commit ID, or commit messages
- test_status   → questions about whether a feature was tested, or its pass/fail result or the test name

QUESTION:
{question}

INTENT:
"""
