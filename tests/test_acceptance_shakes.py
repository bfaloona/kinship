import unittest
from kinship.parser import Parser

class TestShakespeareValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the GEDCOM file and parse it
        cls.parser = Parser("data/shakespeare.ged")
        cls.parser.parse()

        # Use the parser's relationships and families attributes directly
        cls.relationships = cls.parser.get_relationships()
        cls.families = cls.parser.families

    def test_parent_child_relationships(self):
        # Verify a known parent-child relationship
        parent_child = [rel for rel in self.relationships if rel['Source'] == 'I0003' and rel['Target'] == 'I0001' and rel['Relationship'] == 'parent-child']
        self.assertTrue(parent_child, "John Shakespeare (I0003) should be a parent of William Shakespeare (I0001)")

    def test_spousal_relationship(self):
        # Verify a known spousal relationship
        spouses = [rel for rel in self.relationships if rel['Source'] == 'I0003' and rel['Target'] == 'I0002' and rel['Relationship'] == 'spouse']
        self.assertTrue(spouses, "John Shakespeare (I0003) should be a spouse of Mary Arden (I0002)")

    def test_sibling_relationship(self):
        # Verify a known sibling relationship
        siblings = [rel for rel in self.relationships if rel['Source'] == 'I0001' and rel['Target'] == 'I0008' and rel['Relationship'] == 'sibling']
        self.assertTrue(siblings, "William Shakespeare (I0001) should be a sibling of Joan Shakespeare (I0008)")

    def test_step_parent_relationship(self):
        # Verify a known step-parent relationship
        step_parent = [rel for rel in self.relationships if rel['Source'] == 'I0004' and rel['Target'] == 'I9998' and rel['Relationship'] == 'step-parent']
        self.assertTrue(step_parent, "Anne Hathaway (I0004) should be a step-parent of Edward Shakespeare (I9998)")

    def test_families(self):
        # Verify the new family (F012) with step-parent relationship exists in families
        f012_family = [fam for fam in self.families if fam['Family_ID'] == 'F012']
        self.assertTrue(f012_family, "Family F012 should exist in the families.")

        # Verify that William Shakespeare (I0001) appears as a child in F012
        f012_child = [child for child in f012_family[0]['Children'] if child['Child_ID'] == 'I9998']
        self.assertTrue(f012_child, "Edward Shakespeare (I9998) should be a child in Family F012.")

        # Verify Anne Hathaway (I0004) is listed as a spouse in F012
        f012_spouse = f012_family[0]['Wife_ID'] == 'I0004'
        self.assertTrue(f012_spouse, "Anne Hathaway (I0004) should be listed as a spouse in Family F012.")

if __name__ == "__main__":
    unittest.main()