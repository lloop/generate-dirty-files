import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_binary_truncated():
    modifier = UnifiedModifier()
    content = b"x" * 100
    result, label = modifier.transform(content, "bin", is_binary=True, mutation_type="truncated_binary")
    assert label == "truncated_binary"
    assert b"_build_uid:" in result
