import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_csv_none_mutation():
    modifier = UnifiedModifier()
    content = "id,name,value\n1,test,100"
    result, label = modifier.transform(content, "csv", mutation_type="none")
    assert label == "none"
    assert "id,name,value" in result
    assert "# build_id," in result
