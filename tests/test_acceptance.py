from kinship.gedcom_parser import GedcomParser
from unittest.mock import patch, mock_open


def test_full_parse():
    mock_gedcom_content = (
        "0 HEAD\n0 @I1@ INDI\n1 NAME John /Doe/\n1 SEX M\n1 BIRT\n2 DATE 1990-01-01\n0 TRLR"
    )

    with patch("builtins.open", mock_open(read_data=mock_gedcom_content)):
        parser = GedcomParser("tests/mock_file.ged")
        parser.parse_gedcom_file()

        assert "I1" in parser.individuals
        assert parser.individuals["I1"].full_name == "John Doe"
        assert parser.individuals["I1"].sex == "M"
        assert parser.individuals["I1"].birth_place == "New York"
        assert parser.individuals["I1"].death_place == "Los Angeles"
