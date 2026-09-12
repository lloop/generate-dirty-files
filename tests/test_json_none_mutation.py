import pytest
import json
from data_modifiers.modify_content import UnifiedModifier

def test_json_none_mutation():
    modifier = UnifiedModifier()
    content = '{"key": "value"}'
    result, label = modifier.transform(content, "json", mutation_type="none")
    assert label == "none"
    data = json.loads(result)
    assert "_build_meta" in data
