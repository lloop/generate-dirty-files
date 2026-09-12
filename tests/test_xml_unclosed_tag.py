import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_xml_unclosed_tag():
    modifier = UnifiedModifier()
    content = '<root><item>test</item></root>'
    result, label = modifier.transform(content, "xml", mutation_type="unclosed_tag")
    assert label == "unclosed_tag"
    assert "<_broken_" in result
