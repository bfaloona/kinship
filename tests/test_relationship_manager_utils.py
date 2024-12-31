import unittest
from kinship.relationship_manager import RelationshipManager
from kinship.family_tree_data import FamilyTreeData
from kinship.individual import Individual
from kinship.family import Family

class TestRelationshipManagerUtils(unittest.TestCase):

    def setUp(self):
        # Create a mock family tree
        individuals = {
            'I001': Individual('I001', 'Parent1', sex='M'),
            'I002': Individual('I002', 'Parent2', sex='F'),
            'I003': Individual('I003', 'Child1', sex='M'),
            'I004': Individual('I004', 'Child2', sex='F'),
            'I005': Individual('I005', 'Grandparent', sex='M'),
            'I999': Individual('I999', 'Unrelated', sex='F'),
        }
        families = {
            'F001': Family('F001', husband_id='I005', wife_id=None, children=['I001']),
            'F002': Family('F002', husband_id='I001', wife_id='I002', children=['I003', 'I004'])
        }
        self.data = FamilyTreeData()
        self.data._load_from_objs(individuals, families)
        self.manager = RelationshipManager(self.data)

    def test_bfs_to_ancestors(self):
        # Test basic ancestor traversal
        ancestors = self.manager._bfs_to_ancestors('I003')
        self.assertEqual(1, ancestors['I001'])  # Parent
        self.assertEqual(2, ancestors['I005'])  # Grandparent

    def test_bfs_to_ancestors_unrelated(self):
        # Test unrelated individual
        unrelated_ancestors = self.manager._bfs_to_ancestors('I999')
        self.assertEqual({'I999': 0}, unrelated_ancestors)

    def test_bfs_to_ancestors_invalid(self):
        # Test missing ID
        with self.assertRaises(ValueError):
            self.manager._bfs_to_ancestors('INVALID_ID')

    def test_bfs_to_ancestors_10_gen(self):
        # Test 10 levels of ancestors
        for i in range(6, 14):
            self.data.individuals[f'I00{i}'] = Individual(f'I00{i}', f'Ancestor{i}')
            self.data.families[f'F00{i}'] = Family(f'F00{i}', husband_id=f'I00{i}', wife_id=None, children=[f'I00{i-1}'])
        ancestors = self.manager._bfs_to_ancestors('I001')
        self.assertEqual(10, len(ancestors))  # 10 generations

    def test_find_closest_common_ancestor_parent(self):
        # Test finding the closest common ancestor
        ancestors_1 = self.manager._bfs_to_ancestors('I003')
        ancestors_2 = self.manager._bfs_to_ancestors('I004')
        cca, ref_distance, related_distance = self.manager._find_closest_common_ancestor(ancestors_1, ancestors_2)

        self.assertTrue(cca in ['I001', 'I002'])
        self.assertEqual(1, ref_distance)
        self.assertEqual(1, related_distance)

    def test_find_closest_common_ancestor_negative(self):
        # Test unrelated individuals
        unrelated_1 = self.manager._bfs_to_ancestors('I003')
        unrelated_2 = self.manager._bfs_to_ancestors('I999')
        cca, ref_distance, related_distance = self.manager._find_closest_common_ancestor(unrelated_1, unrelated_2)
        self.assertIsNone(cca)
        self.assertIsNone(ref_distance)
        self.assertIsNone(related_distance)

    def test_find_closest_common_ancestor_missing(self):
        # Test one individual missing ancestors
        ancestors_1 = self.manager._bfs_to_ancestors('I003')
        result = self.manager._find_closest_common_ancestor(ancestors_1, {})
        self.assertTrue({None, None, None}, result)
