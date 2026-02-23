import re

SECRET_PATTERNS = {
    "ICE": r"\b\d{15}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "TOKEN": r"\b[A-Za-z0-9_\-]{20,}\b",
}


def sanitize_text(text: str):
    secrets = {}

    for name, pattern in SECRET_PATTERNS.items():
        matches = re.findall(pattern, text)
        for i, match in enumerate(matches):
            placeholder = f"<{name}_{i}>"
            secrets[placeholder] = match
            text = text.replace(match, placeholder)

    return text, secrets