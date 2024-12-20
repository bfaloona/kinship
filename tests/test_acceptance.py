from main import GedcomParser
from unittest.mock import patch, mock_open


def test_full_parse():
    mock_gedcom_content = (
        "0 HEAD\n0 @I1@ INDI\n1 NAME John /Doe/\n1 BIRT\n2 DATE 1990-01-01\n0 TRLR"
    )

    with patch("builtins.open", mock_open(read_data=mock_gedcom_content)):
        parser = GedcomParser("tests/mock_file.ged")
        parser.parse()

        assert "I1" in parser.individuals
        assert parser.individuals["I1"].full_name == "John Doe"
