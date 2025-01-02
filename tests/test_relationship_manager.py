import unittest
from kinship.relationship_manager import RelationshipManager
from kinship.family_tree_data import FamilyTreeData
from kinship.individual import Individual
from kinship.family import Family

class TestRelationshipManagerMain(unittest.TestCase):

    def setUp(self):
        # Comprehensive family tree for main tests
        individuals = {
            'I001': Individual('I001', 'Father1', sex='M'),
            'I002': Individual('I002', 'Mother1', sex='F'),
            'I003': Individual('I003', 'Father2', sex='M'),
            'I004': Individual('I004', 'Mother2', sex='F'),
            'I005': Individual('I005', 'Child1', sex='M'),
            'I006': Individual('I006', 'Child2', sex='F'),
            'I007': Individual('I007', 'HalfSibling', sex='F'),
            'I008': Individual('I008', 'StepSibling', sex='M'),
            'I009': Individual('I009', 'StepSibling', sex='U'),
            'I010': Individual('I010', 'Unrelated', sex='M'),
        }

        families = {
            'F001': Family('F001', husband_id='I001', wife_id='I002', children=['I005', 'I006']),
            'F002': Family('F002', husband_id='I001', wife_id=None, children=['I007']),
            'F003': Family('F003', husband_id='I003', wife_id='I004', children=['I008', 'I009']),
            'F004': Family('F004', husband_id='I003', wife_id='I002', children=[])
        }

        data = FamilyTreeData()
        data._load_from_objs(individuals, families)
        self.manager = RelationshipManager(data)

    def test_mother_father_relationships(self):
        self.assertEqual('mother', self.manager.display_relationship('I002', 'I005'))
        self.assertEqual('mother', self.manager.display_relationship('I002', 'I006'))
        self.assertEqual('father', self.manager.display_relationship('I001', 'I005'))
        self.assertEqual('father', self.manager.display_relationship('I001', 'I006'))

    def test_child_relationships_son_daughter(self):
        self.assertEqual('son', self.manager.display_relationship('I005', 'I001'))
        self.assertEqual('daughter', self.manager.display_relationship('I006', 'I001'))
        self.assertEqual('son', self.manager.display_relationship('I005', 'I002'))
        self.assertEqual('daughter', self.manager.display_relationship('I006', 'I002'))

    def test_sibling_relationships_brother_sister(self):
        self.assertEqual('brother', self.manager.display_relationship('I005', 'I006'))
        self.assertEqual('sister', self.manager.display_relationship('I006', 'I005'))

    def test_sibling_relfationships(self):
        self.assertEqual('sibling', self.manager.display_relationship('I009', 'I008'))

    def test_half_sibling_relationships(self):
        self.assertEqual('half-sibling', self.manager.display_relationship('I005', 'I007'))

    def test_step_sibling_relationships(self):
        self.assertEqual('step-sibling', self.manager.display_relationship('I006', 'I008'))

    # @unittest.skip("Not implemented")
    def test_step_parent_relationships(self):
        self.assertEqual('step-parent', self.manager.display_relationship('I003', 'I005'))
        self.assertEqual('step-parent', self.manager.display_relationship('I002', 'I008'))

    def test_cousinship_negative(self):
        # Add more detailed cousinship cases here as needed
        self.assertEqual('No relation', self.manager.calculate_cousinship('I010', 'I005'))

if __name__ == '__main__':
    unittest.main()