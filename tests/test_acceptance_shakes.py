import unittest

from parser.gedcom_parser import GedcomParser


class TestShakespeareValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the GEDCOM file and parse it
        cls.parser = GedcomParser("data/shakespeare.ged")
        cls.parser.parse_gedcom_file()

        # Use the parser's relationships and families attributes directly
        cls.relationships = cls.parser.get_relationships()
        cls.families = cls.parser.families

    # def test_parent_child_relationships(self):
    #     # Verify a known parent-child relationship
    #     parent_child = [rel for rel in self.relationships if rel['Source'] == 'I0003' and rel['Target'] == 'I0001' and rel['Relationship'] == 'parent-child']
    #     self.assertTrue(parent_child, "John Shakespeare (I0003) should be a parent of William Shakespeare (I0001)")
    #
    # def test_spousal_relationship(self):
    #     # Verify a known spousal relationship
    #     spouses = [rel for rel in self.relationships if rel['Source'] == 'I0003' and rel['Target'] == 'I0002' and rel['Relationship'] == 'spouse']
    #     self.assertTrue(spouses, "John Shakespeare (I0003) should be a spouse of Mary Arden (I0002)")
    #
    # def test_sibling_relationship(self):
    #     # Verify a known sibling relationship
    #     siblings = [rel for rel in self.relationships if rel['Source'] == 'I0001' and rel['Target'] == 'I0008' and rel['Relationship'] == 'sibling']
    #     self.assertTrue(siblings, "William Shakespeare (I0001) should be a sibling of Joan Shakespeare (I0008)")
    #
    # def test_step_parent_relationship(self):
    #     # Verify a known step-parent relationship
    #     step_parent = [rel for rel in self.relationships if rel['Source'] == 'I0004' and rel['Target'] == 'I9998' and rel['Relationship'] == 'step-parent']
    #     self.assertTrue(step_parent, "Anne Hathaway (I0004) should be a step-parent of Edward Shakespeare (I9998)")
    #
    # def test_families(self):
    #     # Verify the new family (F012) with step-parent relationship exists in families
    #     f012_family = self.families['F012']
    #     self.assertTrue(f012_family, "Family F012 should exist in the families.")
    #
    #     # Verify that Edward Shakespeare (I9998) appears as a child in F012
    #     # f012_child = (
    #     found = False
    #     for child in f012_family.children:
    #         if child.id == 'I9998':
    #             found = True
    #     self.assertTrue(found, "Edward Shakespeare (I9998) should be a child in Family F012.")
    #
    #     # Verify Anne New (I0004) is listed as a spouse in F012
    #     f012_spouse = False
    #     f012_spouse = (f012_family.wife_id == 'I9999') and (f012_family.wife_name == "Anne New")
    #     self.assertTrue(f012_spouse, "Anne New (I9999) should be listed as a spouse in Family F012.")
    #
    # def test_multiple_marriages(self):
    #     # Verify that John Shakespeare (I0003) has multiple spouses
    #     spouses = [rel for rel in self.relationships if rel['Source'] == 'I0003' and rel['Relationship'] == 'spouse']
    #     self.assertTrue(len(spouses) > 1, "John Shakespeare (I0003) should have multiple spouses.")
    #
    # def test_multiple_children(self):
    #     # Verify that John Shakespeare (I0003) has multiple children
    #     children = [rel for rel in self.relationships if rel['Source'] == 'I0003' and rel['Relationship'] == 'parent-child']
    #     self.assertTrue(len(children) > 1, "John Shakespeare (I0003) should have multiple children.")
    #
    # def test_multiple_siblings(self):
    #     # Verify that William Shakespeare (I0001) has multiple siblings
    #     siblings = [rel for rel in self.relationships if rel['Source'] == 'I0001' and rel['Relationship'] == 'sibling']
    #     self.assertTrue(len(siblings) > 1, "William Shakespeare (I0001) should have multiple siblings.")
    #
    # def test_multiple_step_parents(self):
    #     # Verify that Edward Shakespeare (I9998) has multiple step-parents
    #     step_parents = [rel for rel in self.relationships if rel['Target'] == 'I9998' and rel['Relationship'] == 'step-parent']
    #     self.assertTrue(len(step_parents) > 1, "Edward Shakespeare (I9998) should have multiple step-parents.")
    #
    # def test_multiple_families(self):
    #     # Verify that William Shakespeare (I0001) has multiple families
    #     families = [family for family in self.families.values() if 'I0001' in family.children]
    #     self.assertTrue(len(families) > 1, "William Shakespeare (I0001) should have multiple families.")
    #
    # def test_multiple_spouses(self):
    #     # Verify that William Shakespeare (I0001) has multiple spouses
    #     spouses = [family for family in self.families.values() if 'I0001' in family.children]
    #     self.assertTrue(len(spouses) > 1, "William Shakespeare (I0001) should have multiple spouses.")
    #
    # def test_multiple_parents(self):
    #     # Verify that William Shakespeare (I0001) has multiple parents
    #     parents = [family for family in self.families.values() if 'I0001' in family.children]
    #     self.assertTrue(len(parents) > 1, "William Shakespeare (I0001) should have multiple parents.")
    #
    # def test_multiple_children_in_family(self):
    #     # Verify that Family F012 has multiple children
    #     f012_family = self.families['F012']
    #     self.assertTrue(len(f012_family.children) > 1, "Family F012 should have multiple children.")
    #
    # def test_one_relationship_per_pair(self):
    #     # Verify that there is only one relationship between any two individuals
    #     relationships = [(rel['Source'], rel['Target']) for rel in self.relationships]
    #     self.assertEqual(len(relationships), len(set(relationships)), "There should be only one relationship between any two individuals.")


if __name__ == "__main__":
    unittest.main()