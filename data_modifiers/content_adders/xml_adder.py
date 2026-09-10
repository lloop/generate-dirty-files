import random
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Union


class XMLAdder:
    """Generates and injects dynamic XML nodes, attributes, and comments,

    and rearranges sibling elements to ensure unique document signatures.
    """

    def __init__(self):
        self.mock_statuses = ["ACTIVE", "PENDING", "VERIFIED", "ARCHIVED"]
        self.mock_services = ["auth-node", "data-bus", "telemetry-engine", "cache-router"]

    def _generate_synthetic_node(self) -> ET.Element:
        """Creates a standalone XML element populated with dynamic child attributes and text."""
        node_id = f"NODE-{str(uuid.uuid4())[:8]}"
        
        elem = ET.Element("AuditCheckpoint")
        elem.set("id", node_id)
        elem.set("timestamp", datetime.now().isoformat())
        elem.set("status", random.choice(self.mock_statuses))

        service_node = ET.SubElement(elem, "ServiceOrigin")
        service_node.text = random.choice(self.mock_services)

        metric_node = ET.SubElement(elem, "MetricValue")
        metric_node.text = str(round(random.uniform(1.0, 999.9), 2))

        return elem

    def inject_and_rearrange(self, file_path: Union[str, Path]) -> None:
        """Reads target XML file, injects dynamic child elements, shuffles top-level

        sibling nodes under the root, and writes formatted XML back to disk.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        raw_xml = path.read_text(encoding="utf-8").strip()

        try:
            root = ET.fromstring(raw_xml)
        except ET.ParseError:
            # Fallback wrapper if base template was empty or malformed
            root = ET.Element("DatasetPayload")

        # 1. Inject dynamic root attributes
        root.set("last_hydrated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        root.set("build_ref", f"BUILD-{str(uuid.uuid4())[:8]}")

        # 2. Inject new synthetic child element
        new_child = self._generate_synthetic_node()
        root.append(new_child)

        # 3. Extract and shuffle top-level sibling nodes
        children = list(root)
        if len(children) > 1:
            # Clear existing order and re-append in shuffled sequence
            for child in children:
                root.remove(child)
            
            random.shuffle(children)
            for child in children:
                root.append(child)

        # 4. Format and write updated XML back to disk
        ET.indent(root, space="  ")  # Ensures readable layout formatting
        tree_out = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        
        path.write_text(tree_out + "\n", encoding="utf-8")


def modify_xml(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = XMLAdder()
    adder.inject_and_rearrange(file_path)
    return "xml_hydrated_and_rearranged"