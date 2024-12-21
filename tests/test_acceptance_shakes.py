import unittest
import pandas as pd
from kinship.parser import Parser

class TestShakespeareValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the GEDCOM file and parse it
        cls.parser = Parser("data/shakespeare.ged")
        cls.parser.parse()

        # Load the generated output files
        cls.network_graph_path = "output/network_graph_shakespeare_2024Dec20.csv"
        cls.families_file_path = "output/families_shakespeare_2024Dec20.csv"
        cls.network_graph_df = pd.read_csv(cls.network_graph_path)
        cls.families_df = pd.read_csv(cls.families_file_path)

    def test_parent_child_relationships(self):
        # Verify a known parent-child relationship
        parent_child = self.network_graph_df[(self.network_graph_df['Source'] == 'I0003') &
                                             (self.network_graph_df['Target'] == 'I0001') &
                                             (self.network_graph_df['Relationship'] == 'parent-child')]
        self.assertFalse(parent_child.empty, "John Shakespeare (I0003) should be a parent of William Shakespeare (I0001)")

    def test_spousal_relationship(self):
        # Verify a known spousal relationship
        spouses = self.network_graph_df[(self.network_graph_df['Source'] == 'I0003') &
                                        (self.network_graph_df['Target'] == 'I0002') &
                                        (self.network_graph_df['Relationship'] == 'spouse')]
        self.assertFalse(spouses.empty, "John Shakespeare (I0003) should be a spouse of Mary Arden (I0002)")

    def test_sibling_relationship(self):
        # Verify a known sibling relationship
        siblings = self.network_graph_df[(self.network_graph_df['Source'] == 'I0001') &
                                         (self.network_graph_df['Target'] == 'I0008') &
                                         (self.network_graph_df['Relationship'] == 'sibling')]
        self.assertFalse(siblings.empty, "William Shakespeare (I0001) should be a sibling of Joan Shakespeare (I0008)")

    def test_step_parent_relationship(self):
        # Verify a known step-parent relationship
        step_parent = self.network_graph_df[(self.network_graph_df['Source'] == 'I0004') &
                                            (self.network_graph_df['Target'] == 'I0001') &
                                            (self.network_graph_df['Relationship'] == 'step-parent')]
        self.assertFalse(step_parent.empty, "Anne Hathaway (I0004) should be a step-parent of William Shakespeare (I0001)")

    def test_families_file(self):
        # Verify the new family (F012) with step-parent relationship exists in families file
        f012_family = self.families_df[self.families_df['Family_ID'] == 'F012']
        self.assertFalse(f012_family.empty, "Family F012 should exist in the families file.")

        # Verify that William Shakespeare (I0001) appears as a child in F012
        f012_child = f012_family[f012_family['Child_ID'] == 'I0001']
        self.assertFalse(f012_child.empty, "William Shakespeare (I0001) should be a child in Family F012.")

        # Verify Anne Hathaway (I0004) is listed as a spouse in F012
        f012_spouse = f012_family[f012_family['Wife_ID'] == 'I0004']
        self.assertFalse(f012_spouse.empty, "Anne Hathaway (I0004) should be listed as a spouse in Family F012.")

if __name__ == "__main__":
    unittest.main()