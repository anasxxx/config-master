from __future__ import annotations
from datetime import datetime
from typing import Any, Dict


SOURCE_RANK = {
    "llm": 1,
    "rules": 1,
    "autofill": 2,
    "menu": 3,
    "user": 4,
}


def normalize_source(source: str) -> str:
    s = (source or "").strip().lower()
    if s in {"regex", "rule"}:
        return "rules"
    if s in {"tool", "default"}:
        return "autofill"
    if s not in SOURCE_RANK:
        return "rules"
    return s


def is_value_object(x: Any) -> bool:
    return isinstance(x, dict) and "value" in x and "source" in x


def is_authoritative(existing_source: str, new_source: str) -> bool:
    e = SOURCE_RANK.get(normalize_source(existing_source), 0)
    n = SOURCE_RANK.get(normalize_source(new_source), 0)
    return n > e


def _traverse_get(obj: Any, path: str):
    cur = obj
    for part in (path or "").split("."):
        if part.isdigit():
            idx = int(part)
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
    return cur


def _ensure_list_index(lst: list, idx: int, default_item: Any):
    while len(lst) <= idx:
        lst.append(default_item if default_item is not None else {})


def _traverse_set(obj: Any, path: str, payload: Any):
    parts = (path or "").split(".")
    if not parts:
        return False
    cur = obj
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        if part.isdigit():
            idx = int(part)
            if not isinstance(cur, list):
                return False
            _ensure_list_index(cur, idx, {})
            if last:
                cur[idx] = payload
                return True
            if not isinstance(cur[idx], (dict, list)):
                cur[idx] = {}
            cur = cur[idx]
            continue
        if not isinstance(cur, dict):
            return False
        if last:
            cur[part] = payload
            return True
        if part not in cur or cur[part] is None:
            cur[part] = {}
        cur = cur[part]
    return False


def get_value(facts: Dict[str, Any], path: str):
    node = _traverse_get(facts, path)
    if is_value_object(node):
        return node.get("value")
    return node


def get_meta(facts: Dict[str, Any], path: str) -> Dict[str, Any]:
    node = _traverse_get(facts, path)
    if is_value_object(node):
        return {
            "source": normalize_source(str(node.get("source") or "")),
            "confidence": float(node.get("confidence") or 0.0),
            "updated_at": node.get("updated_at"),
            "evidence": node.get("evidence"),
        }
    return {}


def set_value(
    facts: Dict[str, Any],
    path: str,
    value: Any,
    source: str,
    confidence: float,
    evidence: str | None = None,
) -> bool:
    src = normalize_source(source)
    try:
        conf = float(confidence)
    except Exception:
        conf = 0.0
    conf = max(0.0, min(1.0, conf))

    payload = {
        "value": value,
        "source": src,
        "confidence": conf,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    if evidence:
        payload["evidence"] = evidence
    return _traverse_set(facts, path, payload)


def unwrap_facts(node: Any):
    if is_value_object(node):
        return unwrap_facts(node.get("value"))
    if isinstance(node, dict):
        return {k: unwrap_facts(v) for k, v in node.items()}
    if isinstance(node, list):
        return [unwrap_facts(x) for x in node]
    return node
