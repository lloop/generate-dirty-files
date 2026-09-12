import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_csv_swapped_delimiter():
    modifier = UnifiedModifier()
    content = "id,name\n1,test"
    result, label = modifier.transform(content, "csv", mutation_type="swapped_delimiter")
    assert label == "swapped_delimiter"
    assert ";" in result
