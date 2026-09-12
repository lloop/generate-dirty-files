import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_csv_dropped_header():
    modifier = UnifiedModifier()
    content = "id,name,value\n1,test,100"
    result, label = modifier.transform(content, "csv", mutation_type="dropped_header")
    assert label == "dropped_header"
    assert "id,name,value" not in result
    assert "1,test,100" in result
