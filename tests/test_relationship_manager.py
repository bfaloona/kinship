import unittest
import kinship.relationship_manager as rm
import kinship.individual as ind
import kinship.family as f
from kinship.family_tree_data import FamilyTreeData

class TestRelationshipManager(unittest.TestCase):

    def setUp(self):
        # Sample data matching parser structures
        self.individuals = {
            'I999': ind.Individual('I999', 'Great Grandpa I001', sex='M', birth_date='1890-11-11',
                                   birth_place='New York, USA', death_date='1965-02-15', death_place='New York, USA'),
            'I001': ind.Individual('I001', 'Grandpa I001', sex='M', birth_date='1920-01-01',
                                   birth_place='New York, USA', death_date='1995-06-15', death_place='New York, USA'),
            'I002': ind.Individual('I002', 'Grandma I002', sex='F', birth_date='1925-02-14', birth_place='Boston, USA',
                                   death_date='2000-09-21'),
            'I003': ind.Individual('I003', 'Son I001', sex='M', birth_date='1950-05-20', birth_place='Chicago, USA'),
            'I004': ind.Individual('I004', 'Daughter I001', sex='F', birth_date='1952-07-10',
                                   birth_place='Los Angeles, USA'),
            'I005': ind.Individual('I005', "Son's Wife I005", sex='F', birth_date='1955-11-02',
                                   birth_place='San Francisco, USA'),
            'I006': ind.Individual('I006', 'Grandson I001', sex='M', birth_date='1980-03-15',
                                   birth_place='Seattle, USA'),
            'I007': ind.Individual('I007', "Daughter's Husband I007", sex='M', birth_date='1949-09-30',
                                   birth_place='Denver, USA'),
            'I008': ind.Individual('I008', 'Grandson, Uncle and Brother I007', sex='M', birth_date='1985-04-25'),
            'I009': ind.Individual('I009', 'Granddaughter, Stepdaughter and Sister I007', sex='F',
                                   birth_date='1987-08-17', birth_place='Austin, USA'),
            'I010': ind.Individual('I010', "Granddaughter's Husband and Stepdad I010", sex='M', birth_date='1975-12-01',
                                   birth_place='Phoenix, USA', death_date='2050-01-01', death_place='Phoenix, USA'),
            'I011': ind.Individual('I011', 'Great-grandson I010', sex='M', birth_date='2010-02-28',
                                   birth_place='Dallas, USA'),
            'I998': ind.Individual('I998', 'Daughter I001\'s Husband I998', sex='M', birth_date='2020-02-10',
                                   birth_place='Austin, USA'),
            'I997': ind.Individual('I997', 'Great-grandson I998', sex='M', birth_date='2020-02-78',
                                   birth_place='El Paso, USA'),
        }

        self.families = {
            'F999': f.Family('F999', 'I999', 'Great Grandpa I001', None, None, '1 JAN 1920',
                             ['I001']),
            'F001': f.Family('F001', 'I001', 'Grandpa I001', 'I002', 'Grandma I002', '1 JAN 1950',
                             ['I003', 'I004']),
            'F002': f.Family('F002', 'I003', 'Son I001', 'I005', 'Son\'s Wife I005', '10 JUN 1980',
                             ['I006']),
            'F003': f.Family('F003', 'I998', 'Daughter I001\'s Husband I998', 'I004', 'Daughter I001', '10 JUN 2010',
                             ['I997']),
            'F004': f.Family('F004', 'I003', 'Son I001', None, None, '1 JAN 1985',
                             ['I009']),
        }

        data = FamilyTreeData()
        data._load_from_objs(self.individuals, self.families)
        self.manager = rm.RelationshipManager(data)

    def test_bfs_ancestors(self):
        expected_ancestors = {'I001': 1, 'I002': 1, 'I999': 2}
        ancestors = self.manager._bfs_ancestors('I003')
        self.assertEqual(expected_ancestors, ancestors)

    def test_bfs_ancestors_no_ancestors(self):
        expected_ancestors = {}
        ancestors = self.manager._bfs_ancestors('I999')
        self.assertEqual(expected_ancestors, ancestors)

    def test_bfs_ancestors_multiple_generations(self):
        expected_ancestors = {'I003': 1, 'I005': 1, 'I001': 2, 'I002': 2, 'I999': 3}
        ancestors = self.manager._bfs_ancestors('I006')
        self.assertEqual(expected_ancestors, ancestors)

    def test_bfs_ancestors_with_spouse(self):
        expected_ancestors = {'I001': 1, 'I002': 1, 'I999': 2}
        ancestors = self.manager._bfs_ancestors('I004')
        self.assertEqual(expected_ancestors, ancestors)

    def test_bfs_ancestors_with_invalid_id(self):
        expected_ancestors = {}
        ancestors = self.manager._bfs_ancestors('INVALID_ID')
        self.assertEqual(expected_ancestors, ancestors)

    def test_get_relationship_father(self):
        self.assertEqual('father', self.manager.get_relationship('I001', 'I003'))

    def test_get_relationship_child(self):
        self.assertEqual('child', self.manager.get_relationship('I003', 'I001'))

    def test_get_relationship_grandfather(self):
        self.assertEqual('grandfather', self.manager.get_relationship('I001', 'I006'))

    def test_get_relationship_parents(self):
        self.assertEqual('child', self.manager.get_relationship('I003', 'I001'))

    def test_get_parents(self):
        self.assertEqual({'I001', 'I002'}, set(self.manager.data.get_parents('I003')))

    def test_get_relationship_children(self):
        self.assertEqual('father', self.manager.get_relationship('I001', 'I003'))

    def test_get_relationship_spouse(self):
        self.assertEqual('spouse', self.manager.get_relationship('I001', 'I002'))
        # inverted
        self.assertEqual('spouse', self.manager.get_relationship('I002', 'I001'))

    def test_get_relationship_cousin(self):
        self.assertEqual('1th cousin', self.manager.get_relationship('I006', 'I997'))

    def test_bfs_ancestors_biological(self):
        expected_ancestors = {'I003': 1, 'I005': 1, 'I001': 2, 'I002': 2, 'I999': 3}
        ancestors = self.manager._bfs_ancestors('I006')
        self.assertEqual(expected_ancestors, ancestors)

    def test_get_relationship_half_siblings(self):
        self.assertEqual('half-sibling', self.manager.get_relationship('I006', 'I009'))

    def test_get_relationship_step_siblings(self):
        self.assertEqual('step-sibling', self.manager.get_relationship('I006', 'I008'))

    def test_invalid_relationship(self):
        self.assertEqual('No relationship found.', self.manager.get_relationship('I003', 'I010'))

if __name__ == '__main__':
    unittest.main()