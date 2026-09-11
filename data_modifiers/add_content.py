from pathlib import Path
from typing import Union
import uuid
import json

from .content_adders.csv_adder import CSVAdder
from .content_adders.html_adder import HTMLAdder
from .content_adders.jpg_adder import JPGAdder
from .content_adders.json_adder import JSONAdder
from .content_adders.py_adder import PythonAdder
from .content_adders.txt_adder import TXTAdder
from .content_adders.xml_adder import XMLAdder


class ContentVariator:
    """Coordinates extension-specific adders to variate raw file content in memory."""

    def __init__(self):
        self.csv_adder = CSVAdder()
        self.html_adder = HTMLAdder()
        self.jpg_adder = JPGAdder()
        self.json_adder = JSONAdder()
        self.py_adder = PythonAdder()
        self.txt_adder = TXTAdder()
        self.xml_adder = XMLAdder()

    def variate(self, raw_content: Union[str, bytes], extension: str) -> Union[str, bytes]:
        """Routes raw in-memory content to the correct adder based on extension

        and returns the modified content payload.
        """
        ext = extension.lower()

        # Binary format handling
        if ext in [".jpg", ".jpeg"]:
            if isinstance(raw_content, str):
                raw_content = raw_content.encode("latin1")
            payload = self.jpg_adder._generate_synthetic_binary_payload()
            return raw_content + payload

        # Text format handling
        if isinstance(raw_content, bytes):
            raw_content = raw_content.decode("utf-8", errors="ignore")

        if ext == ".csv":
            return self._variate_csv(raw_content)
        elif ext in [".html", ".htm"]:
            return self._variate_html(raw_content)
        elif ext == ".json":
            return self._variate_json(raw_content)
        elif ext == ".py":
            return self._variate_py(raw_content)
        elif ext == ".xml":
            return self._variate_xml(raw_content)
        elif ext == ".txt":
            return self._variate_txt(raw_content)

        return raw_content

    def _variate_csv(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        new_rows = self.csv_adder.generate_random_block(
            num_rows=4, include_header=False
        )

        # Dynamic entropy value to guarantee unique SHA-256 binary hash
        unique_id = uuid.uuid4().hex[:8]

        if not lines:
            header = "record_id,timestamp,user_email,department,amount,status"
            return "\n".join([header] + new_rows) + f"\n# build_id,{unique_id}\n"

        header = lines[0]
        body = lines[1:] + new_rows

        # Append a commented metadata row or append the ID to the last row
        return "\n".join([header] + body) + f"\n# build_id,{unique_id}\n"

    def _variate_html(self, text: str) -> str:
        meta = self.html_adder._generate_meta_tag()
        section = self.html_adder._generate_synthetic_section()

        # Dynamic entropy token to prevent deterministic hash collisions
        unique_token = f"<!-- build_id: {uuid.uuid4().hex} -->"

        if "</head>" in text:
            text = text.replace("</head>", f"  {meta}\n</head>", 1)
        else:
            text = f"{meta}\n{text}"

        if "</body>" in text:
            text = text.replace(
                "</body>", f"{section}\n  {unique_token}\n</body>", 1
            )
        else:
            text += f"\n{section}\n{unique_token}"

        return text

    def _variate_json(self, text: str) -> str:
        try:
            data = json.loads(text) if text.strip() else {}
        except json.JSONDecodeError:
            data = {}

        data = self.json_adder._hydrate_and_rearrange_node(data)

        # Ensure the root structure is a dict so we can inject metadata
        if isinstance(data, dict):
            data["_build_meta"] = {"uid": uuid.uuid4().hex[:8]}
        elif isinstance(data, list):
            data.append({"_build_meta": {"uid": uuid.uuid4().hex[:8]}})

        return json.dumps(data, indent=2)

    def _variate_py(self, text: str) -> str:
        comment = self.py_adder._generate_synthetic_comment()
        var_def = self.py_adder._generate_synthetic_variable()
        func_def = self.py_adder._generate_synthetic_function()
        return f"{comment}\n{var_def}\n\n{text}\n\n{func_def}\n"

    def _variate_xml(self, text: str) -> str:
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(text.strip())
        except ET.ParseError:
            root = ET.Element("DatasetPayload")
        root.append(self.xml_adder._generate_synthetic_node())
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8") + "\n"

    def _variate_txt(self, text: str) -> str:
        header = self.txt_adder._generate_synthetic_header()
        para = self.txt_adder._generate_synthetic_paragraph()
        return f"{header}\n\n{text}\n\n{para}\n"


# Functional interface for direct pipeline calls
_variator = ContentVariator()

def variate_template_content(raw_content: Union[str, bytes], extension: str) -> Union[str, bytes]:
    """Variates template content directly in memory before writing to disk."""
    return _variator.variate(raw_content, extension)