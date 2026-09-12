import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_fallback_none_mutation():
    modifier = UnifiedModifier()
    content = "plain text content"
    result, label = modifier.transform(content, "txt", mutation_type="none")
    assert label == "none"
    assert "# build_id:" in result
    assert content in result
