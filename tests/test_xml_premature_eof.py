import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_xml_premature_eof():
    modifier = UnifiedModifier()
    content = '<root><item>test</item></root>'
    result, label = modifier.transform(content, "xml", mutation_type="premature_eof")
    assert label == "premature_eof"
    assert len(result) < len(content) + 50
