import random
import xml.etree.ElementTree as ET
from .base import BaseFormatHandler


class XMLHandler(BaseFormatHandler):

    def add_unique_entropy(
        self,
        content: str | bytes,
        token: str,
        corruption_label: str = "none",
    ) -> str:
        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        # If the XML has already been structurally corrupted,
        # inject the token without attempting to parse/repair the document.
        if corruption_label != "none":
            comment = f"<!-- meta_uid: {token} -->\n"

            if text.lstrip().startswith("<?xml"):
                declaration_end = text.find("?>")

                if declaration_end != -1:
                    insertion_point = declaration_end + 2
                    return (
                        text[:insertion_point]
                        + "\n"
                        + comment
                        + text[insertion_point:]
                    )

            return comment + text

        # Normal, uncorrupted XML.
        has_decl = text.strip().startswith("<?xml")

        try:
            root = ET.fromstring(text)

            comment = ET.Comment(f" meta_uid: {token} ")
            root.insert(0, comment)

            res = ET.tostring(
                root,
                encoding="utf-8"
            ).decode("utf-8")

            if has_decl and not res.startswith("<?xml"):
                res = '<?xml version="1.0" encoding="utf-8"?>\n' + res

            return res

        except ET.ParseError:
            return text
        
        
        text = content.decode("utf-8", errors="surrogateescape") if isinstance(content, bytes) else content
        
        has_decl = text.strip().startswith("<?xml")
        try:
            root = ET.fromstring(text)
            comment = ET.Comment(f" meta_uid: {token} ")
            root.insert(0, comment)
            res = ET.tostring(root, encoding="utf-8").decode("utf-8")
            if has_decl and not res.startswith("<?xml"):
                res = '<?xml version="1.0" encoding="utf-8"?>\n' + res
            return res
        except ET.ParseError:
            return text + f"\n<!-- meta_uid: {token} -->\n"
    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        mutations = ["premature_eof", "unclosed_tag", "zero_byte"]

        label = random.choice(mutations) if mutation_type == "auto" else "none"

        # Locate the protected unique-token comment.
        token_start = text.find("<!-- meta_uid:")
        token_end = text.find("-->", token_start)

        if token_start != -1 and token_end != -1:
            token_end += 3
        else:
            token_start = -1
            token_end = -1

        if label == "zero_byte":
            return "", label
        elif label == "premature_eof":
            cut_point = max(10, len(text) // 2)

            # Do not truncate through or before the protected token.
            if token_end != -1 and cut_point <= token_end:
                if token_end < len(text) - 1:
                    cut_point = random.randint(token_end + 1, len(text) - 1)
                else:
                    return text, "none"

            return text[:cut_point], label
        elif label == "unclosed_tag":
            if token_start != -1:
                before = text[:token_start]
                protected_token = text[token_start:token_end]
                after = text[token_end:]

                after = after.replace("</", "<", 1)

                return before + protected_token + after, label

            return text.replace("</", "<", 1), label

        return text, label