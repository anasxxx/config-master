# tools.py
from typing import Callable, Dict, Any

from agents.conversation_agent import apply_user_message_to_facts
from agents.auto_fill_rules import auto_fill

TOOLS: Dict[str, Callable[..., Any]] = {}


def tool(name: str):
    def decorator(fn: Callable[..., Any]):
        TOOLS[name] = fn
        return fn
    return decorator


def call_tool(name: str, **kwargs):
    if name not in TOOLS:
        raise ValueError(f"Tool '{name}' not found")
    return TOOLS[name](**kwargs)


@tool("extract_fields")
def extract_fields(state: dict, template_obj: dict, user_text: str):
    apply_user_message_to_facts(state, template_obj, user_text)
    return {"status": "ok"}


@tool("autofill")
def autofill(state: dict):
    before = repr(state["facts"])
    auto_fill(state["facts"])
    after = repr(state["facts"])
    return {"status": "ok", "changed": before != after}
