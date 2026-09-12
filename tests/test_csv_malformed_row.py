import pytest
from data_modifiers.modify_content import UnifiedModifier

def test_csv_malformed_row():
    modifier = UnifiedModifier()
    content = "id,name\n1,test"
    result, label = modifier.transform(content, "csv", mutation_type="malformed_row")
    assert label == "malformed_row"
    assert "unmatched,row," in result
