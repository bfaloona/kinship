import unittest
from kinship.relationship_manager import RelationshipManager
from kinship.family_tree_data import FamilyTreeData
from kinship.individual import Individual
from kinship.family import Family

class TestRelationshipManagerSmoke(unittest.TestCase):
    def setUp(self):
        # Sample data for testing
        self.individuals = {
            "I001": Individual(id="I001", full_name="John Doe", sex="M", birth_date="1970-01-01"),
            "I002": Individual(id="I002", full_name="Jane Doe", sex="F", birth_date="1972-02-02"),
            "I003": Individual(id="I003", full_name="Child One", sex="M", birth_date="2000-03-03"),
            "I004": Individual(id="I004", full_name="Child Two", sex="F", birth_date="2002-04-04")
        }
        self.families = {
            "F001": Family(id="F001", husband_id="I001", wife_id="I002", children=["I003", "I004"])
        }
        self.data = FamilyTreeData()
        self.data.individuals = self.individuals
        self.data.families = self.families
        self.manager = RelationshipManager(self.data)

    def test_build_relationship_graph(self):
        self.manager._build_relationship_graph()
        expected_graph = {
            "I001": {"spouse": {"I002"}, "parent": {"I003", "I004"}, "child": set(), "sibling": set(), "half-sibling": set(), "step-sibling": set(), "step-parent": set(), "step-child": set()},
            "I002": {"spouse": {"I001"}, "parent": {"I003", "I004"}, "child": set(), "sibling": set(), "half-sibling": set(), "step-sibling": set(), "step-parent": set(), "step-child": set()},
            "I003": {"child": {"I001", "I002"}, "sibling": {"I004"}, "parent": set(), "spouse": set(), "half-sibling": set(), "step-sibling": set(), "step-parent": set(), "step-child": set()},
            "I004": {"child": {"I001", "I002"}, "sibling": {"I003"}, "parent": set(), "spouse": set(), "half-sibling": set(), "step-sibling": set(), "step-parent": set(), "step-child": set()}
        }
        self.assertEqual(expected_graph, self.manager.relationship_graph)

if __name__ == "__main__":
    unittest.main()