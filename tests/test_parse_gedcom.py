import pytest
from kinship.gedcom_parser import GedcomParser
from kinship.individual import Individual
from unittest.mock import MagicMock

@pytest.fixture
def mock_parser():
    parser = GedcomParser("mock_file.ged")
    parser.individuals = {
        "I1": Individual("I1", "John Doe", "1970-01-01", "New York", None, None),
        "I2": Individual("I2", "Jane Doe", "1975-02-01", "Los Angeles", None, None),
        "I3": Individual("I3", "Jean Doe", "2005-03-01", "Los Angeles", None, None),
        "I4": Individual("I4", "Jay Doe", "2007-04-01", "Los Angeles", None, None)
    }
    return parser

def test_parse_family(mock_parser):
    mock_family = MagicMock()
    mock_family.xref_id = "@F1@"
    mock_family.sub_tag.side_effect = lambda tag: {
        "HUSB": MagicMock(xref_id="@I1@"),
        "WIFE": MagicMock(xref_id="@I2@"),
    }.get(tag)
    mock_family.sub_tags.side_effect = (
        lambda tag: [MagicMock(xref_id="@I3@"), MagicMock(xref_id="@I4@")]
        if tag == "CHIL"
        else []
    )
    mock_family.sub_tag_value.side_effect = (
        lambda tag: "1990-01-01" if tag == "MARR/DATE" else None
    )

    family = mock_parser.parse_family(mock_family)

    assert family.id == "F1"
    assert family.husband_id == "I1"
    assert family.wife_id == "I2"
    assert family.marr_date == "1990-01-01"
    assert len(family.children) == 2
    assert family.children[0] == "I3"
    assert family.children[1] == "I4"

def test_parse_family_no_children(mock_parser):
    mock_family = MagicMock()
    mock_family.xref_id = "@F2@"
    mock_family.sub_tag.side_effect = lambda tag: {
        "HUSB": MagicMock(xref_id="@I1@"),
        "WIFE": MagicMock(xref_id="@I2@"),
    }.get(tag)
    mock_family.sub_tags.side_effect = lambda tag: [] if tag == "CHIL" else []
    mock_family.sub_tag_value.side_effect = lambda tag: "1990-01-01" if tag == "MARR/DATE" else None

    family = mock_parser.parse_family(mock_family)

    assert family.id == "F2"
    assert family.husband_id == "I1"
    assert family.wife_id == "I2"
    assert family.marr_date == "1990-01-01"
    assert len(family.children) == 0

def test_parse_family_no_marriage_date(mock_parser):
    mock_family = MagicMock()
    mock_family.xref_id = "@F3@"
    mock_family.sub_tag.side_effect = lambda tag: {
        "HUSB": MagicMock(xref_id="@I1@"),
        "WIFE": MagicMock(xref_id="@I2@"),
    }.get(tag)
    mock_family.sub_tags.side_effect = lambda tag: [MagicMock(xref_id="@I3@")] if tag == "CHIL" else []
    mock_family.sub_tag_value.side_effect = lambda tag: None

    family = mock_parser.parse_family(mock_family)

    assert family.id == "F3"
    assert family.husband_id == "I1"
    assert family.wife_id == "I2"
    assert family.marr_date == ''
    assert len(family.children) == 1
    assert family.children[0] == "I3"