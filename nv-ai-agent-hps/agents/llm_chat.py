from __future__ import annotations
from typing import Dict, Any

from agents.prompts import GLOBAL_POLICY, PROMPT_CONVERSATION_AGENT, PROMPT_FORM_ASSISTANT
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


def chat_form_assist(user_text: str, current_question: str, missing_preview: str = "") -> str:
    user_block = (
        f"user_message:\n{(user_text or '').strip()}\n\n"
        f"current_question:\n{(current_question or '').strip()}\n\n"
        f"missing_fields_preview:\n{(missing_preview or '').strip()}\n"
    )
    messages = [
        {"role": "system", "content": GLOBAL_POLICY.strip()},
        {"role": "system", "content": PROMPT_FORM_ASSISTANT.strip()},
        {"role": "user", "content": user_block},
    ]
    payload = {"model": LLM_MODEL, "messages": messages, "stream": False}
    raw = _post_llm(payload)
    txt = (raw or "").strip()
    if txt:
        return txt
    if missing_preview:
        return f"Je reste sur la configuration PowerCard. Il manque encore: {missing_preview}."
    return "Je reste sur la configuration PowerCard. Donne-moi la prochaine information demandee."
