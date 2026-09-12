import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_json_missing_comma():
    modifier = UnifiedModifier()
    content = '{"key": "value", "key2": "value2"}'
    result, label = modifier.transform(content, "json", mutation_type="missing_comma")
    assert label == "missing_comma"
