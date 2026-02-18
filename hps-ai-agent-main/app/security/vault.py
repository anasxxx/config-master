import json
from pathlib import Path

VAULT_PATH = Path("data/secret_vault.json")

def load_vault() -> dict:
    if not VAULT_PATH.exists():
        return {}
    return json.loads(VAULT_PATH.read_text(encoding="utf-8"))

def save_vault(vault: dict) -> None:
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VAULT_PATH.write_text(json.dumps(vault, indent=2, ensure_ascii=False), encoding="utf-8")

def store_secret(case_id: str, field: str, value: str) -> None:
    vault = load_vault()
    vault.setdefault(case_id, {})[field] = value
    save_vault(vault)

def get_secret(case_id: str, field: str) -> str | None:
    vault = load_vault()
    return vault.get(case_id, {}).get(field)
