#!/usr/bin/env python3
"""Baseline Python Template for Synthetic Data Pipeline Ingestion Testing."""

import json
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)


def parse_payload(raw_data: str) -> Dict[str, Any]:
    """Parses raw payload data into a structured record."""
    if not raw_data:
        raise ValueError("Payload input cannot be empty.")

    try:
        data = json.loads(raw_data)
        return {"status": "SUCCESS", "payload": data}
    except json.JSONDecodeError as err:
        logging.error("Failed to decode JSON payload: %s", err)
        return {"status": "ERROR", "message": str(err)}


def main() -> None:
    sample_input = '{"user_id": 101, "role": "admin", "active": true}'
    result = parse_payload(sample_input)
    print(f"Execution Result: {result}")


if __name__ == "__main__":
    main()