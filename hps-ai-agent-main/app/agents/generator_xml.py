from pathlib import Path
import xml.etree.ElementTree as ET

def generate_xml(data: dict, out_path: str) -> str:
    root = ET.Element("Integration")

    client = ET.SubElement(root, "Client")
    ET.SubElement(client, "Name").text = data["client"].get("name", "")
    ET.SubElement(client, "ICE").text = data["client"].get("ice", "")
    ET.SubElement(client, "Country").text = data["client"].get("country", "")

    project = ET.SubElement(root, "Project")
    ET.SubElement(project, "Type").text = data["project"].get("type", "")
    ET.SubElement(project, "Environment").text = data["project"].get("environment", "")

    hps = ET.SubElement(root, "HPS")
    for k, v in data.get("hps", {}).items():
        ET.SubElement(hps, k).text = str(v)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)
    return out_path
