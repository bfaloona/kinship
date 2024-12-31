import unittest
from kinship.relationship_manager import RelationshipManager
from kinship.family_tree_data import FamilyTreeData
from kinship.individual import Individual
from kinship.family import Family

class TestRelationshipManagerSmoke(unittest.TestCase):

    def setUp(self):
        # Minimal family tree for smoke test
        individuals = {
            'I001': Individual('I001', 'Father', sex='M'),
            'I002': Individual('I002', 'Mother', sex='F'),
            'I003': Individual('I003', 'Child1', sex='M'),
            'I004': Individual('I004', 'Child2', sex='F')
        }
        families = {
            'F001': Family('F001', husband_id='I001', wife_id='I002', children=['I003', 'I004'])
        }
        data = FamilyTreeData()
        data._load_from_objs(individuals, families)
        self.manager = RelationshipManager(data)

    def test_parent_child_graph(self):
        self.assertEqual('parent-child', self.manager.relationship_graph['I001']['I003']['relationship'])
        self.assertEqual('parent-child', self.manager.relationship_graph['I003']['I001']['relationship'])

    def test_parent_relationships(self):
        self.assertEqual('parent', self.manager.get_relationship('I001', 'I003'))

    def test_child_relationships(self):
        self.assertEqual('child', self.manager.get_relationship('I003', 'I001'))
        self.assertEqual('child', self.manager.get_relationship('I004', 'I002'))

    def test_invalid_id_relationship(self):
        with self.assertRaises(ValueError):
            self.manager.display_relationship('I003', 'BAD_ID')

if __name__ == '__main__':
    unittest.main()
