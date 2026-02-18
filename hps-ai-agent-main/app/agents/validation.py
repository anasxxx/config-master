def validate(data: dict) -> dict:
    data.setdefault("status", {})
    data["status"].setdefault("missing_fields", [])
    data["status"].setdefault("errors", [])
    data["status"].setdefault("is_complete", False)
    data["status"].setdefault("is_valid", False)
    errors = []
    missing = []

    required = [
    ("client.name", data.get("client", {}).get("name")),
    ("client.ice", data.get("client", {}).get("ice")),
    ("client.country", data.get("client", {}).get("country")),
    ("project.type", data.get("project", {}).get("type")),
    ("project.environment", data.get("project", {}).get("environment")),
]


    for path, value in required:
        if not value:
            missing.append(path)

    ice = data.get("client", {}).get("ice", "")
    if ice and len(ice) < 5:
        errors.append("client.ice: format invalide (trop court)")

    data["status"]["missing_fields"] = missing
    data["status"]["errors"] = errors
    data["status"]["is_valid"] = (len(errors) == 0)
    data["status"]["is_complete"] = (len(missing) == 0)
    return data
