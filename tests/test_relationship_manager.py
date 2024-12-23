# Unit tests for find_common_ancestor and calculate_generational_distance
import unittest
import kinship.relationship_manager as rm
import kinship.individual as ind
import kinship.family as f
from types import SimpleNamespace


class TestRelationshipManager(unittest.TestCase):

    def setUp(self):
        # Sample data matching parser structures
        self.individuals = {
            'I1': ind.Individual('I1', 'Alice'),
            'I2': ind.Individual('I2', 'Bob'),
            'I3': ind.Individual('I3', 'Carol'),
            'I4': ind.Individual('I4', 'David'),
            'I5': ind.Individual('I5', 'Eve'),
            'I6': ind.Individual('I6', 'Frank'),
            'I7': ind.Individual('I7', 'Grace')
        }

        self.families = {
            'F1': f.Family('F1', SimpleNamespace(**{"xref_id": "I4", "name": "David"}),
                           SimpleNamespace(**{"xref_id": "I5", "name": "Eve"}), '3 MAR 2000',
                           [SimpleNamespace(**{"id": "I2", "name": "Bob"})]),
            'F2': f.Family('F2', SimpleNamespace(**{"xref_id": "I6", "name": "Frank"}),
                           SimpleNamespace(**{"xref_id": "I7", "name": "Grace"}), '4 MAR 2005',
                           [SimpleNamespace(**{"id": "I3", "name": "Carol"})]),
            'F3': f.Family('F3', SimpleNamespace(**{"xref_id": "I2", "name": "Bob"}),
                           SimpleNamespace(**{"xref_id": "I3", "name": "Carol"}), '5 MAR 2010',
                           [SimpleNamespace(**{"id": "I1", "name": "Alice"})])
        }
        self.relationships = [
            {'individual1': 'I4', 'individual2': 'I2', 'relationship_type': 'parent'},
            {'individual1': 'I5', 'individual2': 'I2', 'relationship_type': 'parent'},
            {'individual1': 'I6', 'individual2': 'I3', 'relationship_type': 'parent'},
            {'individual1': 'I7', 'individual2': 'I3', 'relationship_type': 'parent'},
            {'individual1': 'I2', 'individual2': 'I1', 'relationship_type': 'parent'},
            {'individual1': 'I3', 'individual2': 'I1', 'relationship_type': 'parent'}
        ]
        self.relationship_manager = rm.RelationshipManager(self.individuals, self.families, self.relationships, None)


    def test_find_common_ancestor(self):
        # Test case 1: Common ancestor exists
        self.assertEqual(self.relationship_manager.find_common_ancestor('I1', 'I2'), 'I4')

        # Test case 2: No common ancestor
        self.assertIsNone(self.relationship_manager.find_common_ancestor('I1', 'Unknown'))


    def test_calculate_generational_distance(self):
        # Test case 1: Valid ancestor relationship
        self.assertEqual(self.relationship_manager.calculate_generational_distance('I1', 'I4'), 2)

        # Test case 2: No ancestor relationship
        self.assertEqual(self.relationship_manager.calculate_generational_distance('I1', 'Unknown'), float('inf'))
