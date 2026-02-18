import json
from pathlib import Path

from app.states import State
from app.agents.validation import validate
from app.agents.enrichment import enrich_with_hps
from app.agents.generator_xml import generate_xml
from app.agents.conversation import collect_missing_fields


def load_case(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_case(path: str, data: dict) -> None:
    Path(path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def run(case_path: str) -> dict:
    data = load_case(case_path)

    state = State.VALIDATE
    steps = 0

    while state not in (State.DONE, State.ERROR):
        steps += 1 #max3
        if steps > 50:
            print("🛑 Stop sécurité: trop d'itérations (boucle infinie probable).")
            state = State.ERROR
            break

        print(f"\n=== STATE: {state.value} ===")

        if state == State.VALIDATE:
            data = validate(data)
            print("missing_fields:", data["status"]["missing_fields"])
            print("errors:", data["status"]["errors"])

            if not data["status"]["is_valid"]:
                state = State.ERROR
            elif not data["status"]["is_complete"]:
                state = State.COLLECT
            else:
                state = State.ENRICH

        elif state == State.COLLECT:
            data = collect_missing_fields(data)
            state = State.VALIDATE

        elif state == State.ENRICH:
            data = enrich_with_hps(data)
            print("hps:", data["hps"])
            state = State.GENERATE_XML

        elif state == State.GENERATE_XML:
            xml_path = "data/output/integration.xml"
            data.setdefault("artifacts", {})["xml_path"] = generate_xml(data, xml_path)
            print("XML généré:", data["artifacts"]["xml_path"])
            state = State.DONE

        else:
            print("État inattendu:", state)
            state = State.ERROR

    save_case(case_path, data)
    print("\n✅ FIN:", state.value)
    return data


if __name__ == "__main__":
    run("data/example_case.json")
