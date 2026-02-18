from copy import deepcopy
from app.security.policy import SENSITIVE_FIELDS

def _del_path(d: dict, path: str) -> None:
    parts = path.split(".")
    cur = d
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return
        cur = cur[p]
    if isinstance(cur, dict):
        cur.pop(parts[-1], None)

def sanitize_for_llm(data: dict) -> dict:
    clean = deepcopy(data)
    # On supprime les champs sensibles
    for path in SENSITIVE_FIELDS:
        _del_path(clean, path)
    return clean