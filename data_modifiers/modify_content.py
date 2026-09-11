import json
import random
import uuid


class UnifiedModifier:

    def transform(
        self,
        content: str | bytes,
        ext: str,
        is_binary: bool = False,
        mutation_type: str = "auto",
    ) -> tuple[str | bytes, str]:
        """Routes text or binary data to its format-specific handler."""
        ext = ext.lower().lstrip(".")

        if is_binary:
            return self._process_binary(content, ext, mutation_type)

        handler = getattr(self, f"_process_{ext}", self._process_fallback)
        return handler(content, mutation_type)

    def _process_binary(
        self, content: bytes, ext: str, mutation_type: str
    ) -> tuple[bytes, str]:
        """Applies dynamic byte entropy and optional mutations to binary files."""
        mutations = {
            "none": lambda d: d,
            "flipped_bytes": lambda d: self._flip_random_byte(d),
            "truncated_binary": lambda d: d[: max(10, len(d) // 2)],
        }

        label = (
            random.choice(list(mutations.keys()))
            if mutation_type == "auto"
            else mutation_type
        )
        mutation_func = mutations.get(label, mutations["none"])

        # 1. Apply mutation FIRST (truncation happens here)
        mutated_data = mutation_func(content)

        # 2. Append entropy LAST (guarantees the UUID token is never lost)
        entropy_bytes = uuid.uuid4().bytes
        final_data = mutated_data + b"\x00_build_uid:" + entropy_bytes

        return final_data, label
    def _flip_random_byte(self, data: bytes) -> bytes:
        if len(data) < 10:
            return data
        byte_arr = bytearray(data)
        idx = random.randint(len(byte_arr) // 2, len(byte_arr) - 1)
        byte_arr[idx] ^= 0xFF
        return bytes(byte_arr)

    def _process_csv(self, content: str, mutation_type: str) -> tuple[str, str]:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        token = uuid.uuid4().hex[:8]

        header = lines[0] if lines else "id,timestamp,data,status"
        body = lines[1:] if len(lines) > 1 else []
        body.append(f"rec_{token[:4]},{token[:6]},active_data,OK")

        mutations = {
            "none": lambda h, b: [h] + b,
            "dropped_header": lambda h, b: b,
            "swapped_delimiter": lambda h, b: [line.replace(",", ";") for line in ([h] + b)],
            "malformed_row": lambda h, b: [h] + b + [f"unmatched,row,{token},extra"],
        }

        label = random.choice(list(mutations.keys())) if mutation_type == "auto" else mutation_type
        mutation_func = mutations.get(label, mutations["none"])

        transformed = mutation_func(header, body)
        transformed.append(f"# build_id,{token}")

        return "\n".join(transformed) + "\n", label

    def _process_json(self, content: str, mutation_type: str) -> tuple[str, str]:
        token = uuid.uuid4().hex[:8]
        try:
            data = json.loads(content) if content.strip() else {}
        except json.JSONDecodeError:
            data = {}

        if isinstance(data, dict):
            data["_build_meta"] = {"uid": token}
        elif isinstance(data, list):
            data.append({"_build_meta": {"uid": token}})

        mutations = ["none", "unclosed_string", "missing_comma"]
        label = random.choice(mutations) if mutation_type == "auto" else mutation_type

        json_str = json.dumps(data, indent=2)

        if label == "unclosed_string":
            json_str = json_str[:-5]
        elif label == "missing_comma":
            json_str = json_str.replace(",", "", 1)

        return json_str, label

    def _process_xml(self, content: str, mutation_type: str) -> tuple[str, str]:
        token = uuid.uuid4().hex[:8]
        mutations = ["none", "premature_eof", "unclosed_tag"]
        label = random.choice(mutations) if mutation_type == "auto" else mutation_type

        base_xml = f"<!-- meta_uid: {token} -->\n" + content

        if label == "premature_eof":
            cut_point = max(10, len(base_xml) // 2)
            return base_xml[:cut_point], label
        elif label == "unclosed_tag":
            return base_xml.replace("</", "<_broken_"), label

        return base_xml, label

    def _process_fallback(self, content: str, mutation_type: str) -> tuple[str, str]:
        """Fallback handler for text files without a dedicated handler."""
        token = uuid.uuid4().hex[:8]
        mutations = ["none", "truncated_text"]
        label = random.choice(mutations) if mutation_type == "auto" else mutation_type

        annotated_content = f"# build_id: {token}\n" + content

        if label == "truncated_text":
            cut_point = max(10, len(annotated_content) // 2)
            return annotated_content[:cut_point], label

        return annotated_content, label