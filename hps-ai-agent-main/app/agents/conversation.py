from app.agents.conversation_ollama import ask_ollama_for_field
from app.security.policy import is_sensitive_field
from app.security.vault import store_secret, get_secret


def collect_missing_fields(data: dict) -> dict:
    missing = data.get("status", {}).get("missing_fields", [])
    if not missing:
        return data

    # identifiant de dossier (pour stocker les secrets par dossier)
    case_id = data.get("case_id", "default_case")

    for field in missing:
        # =========================
        # 1) CHAMPS SENSIBLES : pas de LLM
        # =========================
        if is_sensitive_field(field):
            existing = get_secret(case_id, field)

            if existing:
                value = input(f"{field} (SECRET déjà stocké, Entrée pour garder) : ").strip()
                if not value:
                    value = existing
            else:
                value = input(f"{field} (SECRET) : ").strip()

            # On stocke le secret dans le vault (backend/local)
            store_secret(case_id, field, value)

            # IMPORTANT: on évite de remettre la vraie valeur dans data
            # Pour que la validation passe, on met juste un placeholder
            if field == "client.ice":
                data.setdefault("client", {})["ice"] = "__SECRET__"

            # On passe au champ suivant (on ne fait PAS Ollama)
            continue

        # =========================
        # 2) CHAMPS NON SENSIBLES : Ollama peut proposer
        # =========================
        try:
            suggestion = ask_ollama_for_field(field)
        except Exception:
            suggestion = ""

        if suggestion:
            value = input(f"{field} (suggestion: {suggestion}) : ").strip()
            if not value:
                value = suggestion
        else:
            value = input(f"Veuillez saisir {field}: ").strip()

        # Normalisation simple (optionnel mais utile)
        if field == "project.environment":
            mapping = {"dev": "DEV", "test": "TEST", "prod": "PROD", "production": "PROD"}
            value = mapping.get(value.lower(), value.upper())

        # écrire dans le bon endroit du JSON
        if field == "client.name":
            data.setdefault("client", {})["name"] = value
        elif field == "client.ice":
            data.setdefault("client", {})["ice"] = value
        elif field == "client.country":
            data.setdefault("client", {})["country"] = value
        elif field == "project.type":
            data.setdefault("project", {})["type"] = value
        elif field == "project.environment":
            data.setdefault("project", {})["environment"] = value

    return data
