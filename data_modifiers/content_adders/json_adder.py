import json
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union


class JSONAdder:
    """Generates and injects dynamic JSON fields, populates metadata nodes,

    and shuffles array structures to ensure unique file signatures.
    """

    def __init__(self):
        self.mock_environments = ["staging", "production", "development", "qa-sandbox"]
        self.mock_services = ["auth-service", "data-pipeline", "telemetry-router", "user-store"]

    def _generate_synthetic_node(self) -> Dict[str, Any]:
        """Creates a standalone metadata/audit dictionary."""
        return {
            "build_id": f"BLD-{str(uuid.uuid4())[:8]}",
            "timestamp": datetime.now().isoformat(),
            "environment": random.choice(self.mock_environments),
            "service_origin": random.choice(self.mock_services),
            "telemetry_flag": random.choice([True, False]),
            "session_metric": round(random.uniform(0.1, 99.9), 3),
        }

    def _hydrate_and_rearrange_node(self, data: Any) -> Any:
        """Recursively traverses JSON structures to inject payload data and shuffle lists."""
        if isinstance(data, dict):
            # 1. Capture original keys to prevent infinite recursion on newly injected keys
            original_keys = list(data.keys())
            
            # 2. Recurse through existing dictionary values FIRST
            for key in original_keys:
                if isinstance(data[key], (dict, list)):
                    data[key] = self._hydrate_and_rearrange_node(data[key])
            
            # 3. Inject dynamic metadata node AFTER processing existing keys
            data[f"_system_meta_{random.randint(100, 999)}"] = self._generate_synthetic_node()
            return data

        elif isinstance(data, list):
            # Shuffle list order to vary content layout signature
            if len(data) > 1:
                random.shuffle(data)
            
            # Recurse through list items
            data = [self._hydrate_and_rearrange_node(item) for item in data]
            
            # Optionally append a new synthetic dictionary item to the list
            if random.random() < 0.5:
                data.append(self._generate_synthetic_node())
            return data

        return data
    
    
    def inject_and_rearrange(self, file_path: Union[str, Path]) -> None:
        """Reads target JSON file, injects dynamic keys/objects, shuffles lists,

        and writes formatted JSON back to disk.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        try:
            content = path.read_text(encoding="utf-8").strip()
            data = json.loads(content) if content else {}
        except json.JSONDecodeError:
            # Fallback if base template was empty or malformed
            data = {}

        # If root is a dictionary or list, hydrate it
        if isinstance(data, (dict, list)):
            data = self._hydrate_and_rearrange_node(data)
        else:
            # Wrap primitive root types into a structured payload
            data = {
                "raw_value": data,
                "hydration_meta": self._generate_synthetic_node(),
            }

        # Write formatted JSON back to disk
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def modify_json(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = JSONAdder()
    adder.inject_and_rearrange(file_path)
    return "json_hydrated_and_rearranged"