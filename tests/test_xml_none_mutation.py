import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_xml_none_mutation():
    modifier = UnifiedModifier()
    content = '<root><item>test</item></root>'
    result, label = modifier.transform(content, "xml", mutation_type="none")
    assert label == "none"
    assert content in result
