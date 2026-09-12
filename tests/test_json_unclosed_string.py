import pytest
import json
from data_modifiers.modify_content import UnifiedModifier

def test_json_unclosed_string():
    modifier = UnifiedModifier()
    content = '{"key": "value"}'
    result, label = modifier.transform(content, "json", mutation_type="unclosed_string")
    assert label == "unclosed_string"
    with pytest.raises(json.JSONDecodeError):
        json.loads(result)
