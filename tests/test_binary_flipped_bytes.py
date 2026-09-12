import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_binary_flipped_bytes():
    modifier = UnifiedModifier()
    content = b"x" * 100
    result, label = modifier.transform(content, "bin", is_binary=True, mutation_type="flipped_bytes")
    assert label == "flipped_bytes"
    assert b"_build_uid:" in result
