from __future__ import annotations
from typing import Dict, Any

from agents.prompts import GLOBAL_POLICY, PROMPT_CONVERSATION_AGENT
from agents.llm_extractor import _post_llm  # réutilise ton transport HTTP existant
from config import LLM_MODEL

def chat_explain(user_text: str) -> str:
    messages = [
        {"role": "system", "content": GLOBAL_POLICY.strip()},
        {"role": "system", "content": PROMPT_CONVERSATION_AGENT.strip()},
        {"role": "user", "content": user_text.strip()},
    ]
    payload = {"model": LLM_MODEL, "messages": messages, "stream": False}
    raw = _post_llm(payload)
    return (raw or "").strip()