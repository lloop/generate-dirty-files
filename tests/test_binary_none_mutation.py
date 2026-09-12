import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_binary_none_mutation():
    modifier = UnifiedModifier()
    content = b"test binary data"
    result, label = modifier.transform(content, "bin", is_binary=True, mutation_type="none")
    assert label == "none"
    assert content in result
    assert b"_build_uid:" in result
