import pytest
from kinship.family_tree_data import FamilyTreeData
from kinship.individual import Individual
from kinship.family import Family
from types import SimpleNamespace

@pytest.fixture
def mock_family_tree_data():
    data = FamilyTreeData()
    data.individuals = {
        'I1': Individual('I1', 'John Doe', '1970-01-01', 'New York', None, None),
        'I2': Individual('I2', 'Jane Doe', '1975-02-01', 'Los Angeles', None, None),
        'I3': Individual('I3', 'Jean Doe', '2005-03-01', 'Los Angeles', None, None),
        'I4': Individual('I4', 'Jay Doe', '2007-04-01', 'Los Angeles', None, None)
    }
    data.families = {
        'F1': Family('F1', 'I1', 'John Doe', 'I2', 'Jane Doe', '1990-01-01', ['I3', 'I4'])
    }
    return data

def test_family_tree_data(mock_family_tree_data):
    assert 'I1' in mock_family_tree_data.individuals
    assert 'F1' in mock_family_tree_data.families
    assert mock_family_tree_data.families['F1'].husband_id == 'I1'
    assert mock_family_tree_data.families['F1'].wife_id == 'I2'
    assert len(mock_family_tree_data.families['F1'].children) == 2
    assert mock_family_tree_data.families['F1'].children[0] == 'I3'
    assert mock_family_tree_data.families['F1'].children[1] == 'I4'

def test_load_from_objs():
    individuals = {
        'I1': Individual('I1', 'John Doe', '1970-01-01', 'New York', None, None),
        'I2': Individual('I2', 'Jane Doe', '1975-02-01', 'Los Angeles', None, None)
    }

    families = {
        'F1': Family('F1', SimpleNamespace(xref_id='I1'), SimpleNamespace(xref_id='I2'), '1990-01-01', [])
    }

    data = FamilyTreeData()
    data._load_from_objs(individuals, families)

    assert data.individuals == individuals
    assert data.families == families
