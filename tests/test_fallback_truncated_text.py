import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_fallback_truncated_text():
    modifier = UnifiedModifier()
    content = "x" * 100
    result, label = modifier.transform(content, "txt", mutation_type="truncated_text")
    assert label == "truncated_text"
    assert len(result) < len(content)
