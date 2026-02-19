import os
import json
import oracledb
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

BASE_DIR    = "C:/Users/mahmo/PFE/Config_Master/hps-ai-agent-main/app/dynamic_params"
OUTPUT_FILE = "C:/Users/mahmo/PFE/Config_Master/output_xml/bank_output.xml"

DB_CONFIG = {
    "user":     "username",
    "password": "password",
    "dsn":      "10.110.120.14:1521/PCARD"
}

SYSTEM_PROMPT = """
You are ConfigMaster Agent, responsible for onboarding a new bank into PowerCARD.
You have been given a JSON file containing all the bank parameters.

Your job is to execute the following steps IN ORDER using the available tools:
1. read_latest_json
2. clean_temp_tables
3. load_common_params
4. load_issuer_params
5. generate_catalogue

If any step fails, stop immediately and report the error.
Do NOT skip steps or change their order.
"""


def _get_conn():
    return oracledb.connect(**DB_CONFIG)


def _call_procedure(proc_name: str, params: list) -> str:
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.callproc(proc_name, params)
        conn.commit()
        cursor.close()
        conn.close()
        return f"{proc_name} executed successfully."
    except Exception as e:
        return f"{proc_name} failed: {str(e)}"


def _get_latest_json(directory: str):
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".json")
        and os.path.isfile(os.path.join(directory, f))
        and os.path.getsize(os.path.join(directory, f)) > 0
    ]
    if not files:
        raise FileNotFoundError(f"No valid JSON files found in {directory}")
    latest = max(files, key=os.path.getmtime)
    with open(latest, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            raise ValueError(f"File {latest} is empty.")
        return json.loads(content), latest


def _json2xml(json_obj, line_padding="") -> str:
    result = []
    if isinstance(json_obj, list):
        for item in json_obj:
            result.append(_json2xml(item, line_padding))
        return "\n".join(result)
    if isinstance(json_obj, dict):
        for tag, val in json_obj.items():
            result.append(f"{line_padding}<{tag}>")
            result.append(_json2xml(val, "\t" + line_padding))
            result.append(f"{line_padding}</{tag}>")
        return "\n".join(result)
    return f"{line_padding}{json_obj}"


@tool
def read_latest_json(directory: str = BASE_DIR) -> str:
    """Read the latest JSON file from the dynamic_params directory and extract bank parameters."""
    try:
        data, path = _get_latest_json(directory)

        if data.get("status", {}).get("is_complete") is False:
            return json.dumps({"status": "error", "message": "JSON is not complete yet."})

        bank = data.get("bank", {})
        cards = data.get("cards", [])

        extracted = {
            "bank_code":      bank.get("bank_code"),
            "bank_wording":   bank.get("name"),
            "country_code":   bank.get("country"),
            "local_currency": bank.get("currency"),
            "business_date":  data.get("case_id", "").split("_")[0],
            "resources":      bank.get("resources", []),
            "agencies":       bank.get("agencies", []),
            "cards":          cards,
        }

        missing = [k for k, v in extracted.items() if v is None]
        if missing:
            return json.dumps({
                "status": "error",
                "message": f"Missing required fields: {missing}"
            })

        return json.dumps({"status": "success", "file": path, "data": extracted})

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool
def clean_temp_tables(bank_code: str) -> str:
    """Clear GLB_TEMP and PRODUCT_TEMP tables. Must always be called first."""
    r1 = _call_procedure("pcrd_conv_clean.AUT_CONV_GLB_TEMP_ROLLBACK",     [bank_code])
    r2 = _call_procedure("pcrd_conv_clean.AUT_CONV_PRODUCT_TEMP_ROLLBACK", [bank_code])
    return f"{r1}\n{r2}"


@tool
def load_common_params(bank_code: str, bank_wording: str,
                       business_date: str, local_currency: str,
                       country_code: str) -> str:
    """Load general bank parameters into GLB_TEMP."""
    r1 = _call_procedure("pcrd_board_conv_com.LOAD_BANK_PARAMETERS", [
        bank_code, bank_wording, business_date, local_currency, country_code
    ])
    r2 = _call_procedure("pcrd_board_conv_com.LOAD_BANK_CONV_COM_PARAM", [
        bank_code, business_date
    ])
    return f"{r1}\n{r2}"


@tool
def load_issuer_params(bank_code: str, business_date: str) -> str:
    """Load product parameters into PRODUCT_TEMP then transfer to GLB and PRODUCT tables."""
    return _call_procedure("pcrd_board_conv_iss_param.LOAD_BANK_CONV_ISS_PARAM", [
        bank_code, business_date
    ])


@tool
def generate_catalogue(bank_code: str, business_date: str) -> str:
    """Generate the product catalogue and perform the final COMMIT."""
    return _call_procedure("pcrd_conv_catalogue.MAIN_AUT_POST", [
        bank_code, business_date
    ])


@tool
def save_xml_output(directory: str = BASE_DIR, output_path: str = OUTPUT_FILE) -> str:
    """Convert the latest JSON file to XML and save it to the output path."""
    try:
        data, _ = _get_latest_json(directory)
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + _json2xml(data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return f"XML saved to: {output_path}"
    except Exception as e:
        return f"XML save failed: {str(e)}"


model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    timeout=30,
    num_predict=2000
)

checkpointer = InMemorySaver()

agent = create_react_agent(
    model=model,
    tools=[
        read_latest_json,
        clean_temp_tables,
        load_common_params,
        load_issuer_params,
        generate_catalogue,
        save_xml_output,
    ],
    prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)


if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [{
                "role": "user",
                "content": (
                    f"A new bank needs to be onboarded. "
                    f"Read the latest JSON file from {BASE_DIR}, "
                    f"execute all 5 steps of the Add workflow in order, "
                    f"and save the XML output to {OUTPUT_FILE}."
                )
            }]
        },
        config={"configurable": {"thread_id": "add-action-001"}}
    )

    for msg in result["messages"]:
        print(f"[{msg.type}]: {msg.content}\n")