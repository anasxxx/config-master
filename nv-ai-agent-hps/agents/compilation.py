import os
import json
import re
import xml.etree.ElementTree as ET
import glob
import shutil
from xml.dom import minidom
from typing import Dict, Any, List

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GOALS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "goals"))
SQL_FILE = os.path.join(PROJECT_ROOT, "packages", "PCRD_ST_BOARD_CONV_COM_040610.sql")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output_xml", "bank_output.xml")
temp_json_dir = os.path.join(os.path.dirname(__file__), "temp_json_dir")
temp_sql_dir = os.path.join(os.path.dirname(__file__), "temp_sql_dir")


system_prompt = (
    "You are a data transformation specialist experienced in converting structured data between formats. "
    "Your primary task is to extract configuration parameters from JSON and SQL files, convert them to XML format "
    "with properly nested hierarchical structures, combine both XML outputs into a single consolidated configuration file, "
    "and clean up all temporary working files. Execute each step sequentially using the available tools."
)

model= ChatOllama(model="llama3.2:3b", 
                  temperature=0.7)

def _read_json_impl() -> Dict[str, Any]:
    """Read the most recently modified JSON file from the goals directory and its subdirectories and return its parsed content."""
    json_files = glob.glob(os.path.join(GOALS_DIR, '**', '*.json'), recursive=True)
    if not json_files:
        return {}
    latest_json = max(json_files, key=os.path.getmtime)
    with open(latest_json, 'r', encoding='utf-8') as f:
        return json.load(f)

read_json = tool("extract json params")(_read_json_impl)


def _read_sql_impl() -> List[Dict[str, str]]:
    """Extract PL/SQL assignment parameters (:=) from the SQL file and return them in order."""
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    params: List[Dict[str, str]] = []
    seen = set()
    in_block_comment = False

    for raw_line in sql_content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if in_block_comment:
            if '*/' in line:
                in_block_comment = False
            continue

        if line.startswith('/*'):
            if '*/' not in line:
                in_block_comment = True
            continue

        if line.startswith('--'):
            continue

        line = re.sub(r'--.*$', '', raw_line).strip()
        if ':=' not in line:
            continue

        match = re.match(r'^(?P<lhs>.+?)\s*:=\s*(?P<rhs>[^;]+)', line)
        if not match:
            continue

        key = re.sub(r'\s+', ' ', match.group('lhs')).strip()
        value = re.sub(r'\s+', ' ', match.group('rhs')).strip().rstrip(';')

        if key and value:
            dedup_key = (key, value)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            params.append({"name": key, "value": value})

    return params

read_sql = tool("extract sql params")(_read_sql_impl)



def _json_to_xml_impl() -> str:
    """Convert the latest JSON file to XML, save it in the temporary JSON directory, and return the XML path."""
    json_data = _read_json_impl()
    root = ET.Element("json_parameters")
    def build_xml(parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, key)
                build_xml(child, value)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, "item")
                build_xml(child, item)
        else:
            parent.text = str(data)
    build_xml(root, json_data)
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    os.makedirs(temp_json_dir, exist_ok=True)
    xml_file = os.path.join(temp_json_dir, "json_output.xml")
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    return xml_file

json_to_xml = tool("json to xml converter")(_json_to_xml_impl)


def _sql_to_xml_impl() -> str:
    """Convert extracted SQL parameters to XML, save in the temporary SQL directory, and return the XML path."""
    sql_data = _read_sql_impl()
    root = ET.Element("sql_parameters")
    for item in sql_data:
        param = ET.SubElement(root, "parameter")
        name = ET.SubElement(param, "name")
        name.text = item["name"]
        val = ET.SubElement(param, "value")
        val.text = item["value"]
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    os.makedirs(temp_sql_dir, exist_ok=True)
    xml_file = os.path.join(temp_sql_dir, "sql_output.xml")
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    return xml_file

sql_to_xml = tool("sql to xml converter")(_sql_to_xml_impl)


def _combine_json_sql_to_xml_impl() -> str:
    """Combine JSON and SQL XML files under a root <configuration>, write to OUTPUT_FILE, and return the output path."""
    json_xml_file = os.path.join(temp_json_dir, "json_output.xml")
    sql_xml_file = os.path.join(temp_sql_dir, "sql_output.xml")
    json_tree = ET.parse(json_xml_file)
    sql_tree = ET.parse(sql_xml_file)
    root = ET.Element("configuration")
    json_root = json_tree.getroot()
    sql_root = sql_tree.getroot()
    root.append(json_root)
    root.append(sql_root)
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    return OUTPUT_FILE

combine_json_sql_to_xml = tool("combine json and sql to xml")(_combine_json_sql_to_xml_impl)


def _delete_temp_files_impl() -> str:
    """Delete temporary JSON and SQL directories and return a status message."""
    try:
        if os.path.exists(temp_json_dir):
            shutil.rmtree(temp_json_dir)
        if os.path.exists(temp_sql_dir):
            shutil.rmtree(temp_sql_dir)
        return "Temporary files deleted successfully"
    except Exception as e:
        return f"Error deleting temporary files: {str(e)}"

delete_temp_files = tool("delete temporary files")(_delete_temp_files_impl)


if __name__ == "__main__":
    json_xml_path = _json_to_xml_impl()
    sql_xml_path = _sql_to_xml_impl()
    output_path = _combine_json_sql_to_xml_impl()
    delete_status = _delete_temp_files_impl()
    print(f"JSON XML: {json_xml_path}")
    print(f"SQL XML: {sql_xml_path}")
    print(f"Combined output: {output_path}")
    print(delete_status)
