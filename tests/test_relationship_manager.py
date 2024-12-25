import unittest
import pytest
import kinship.relationship_manager as rm
import kinship.individual as ind
import kinship.family as f
from kinship.family_tree_data import FamilyTreeData

class TestRelationshipManager(unittest.TestCase):

    def setUp(self):
        # Sample data matching parser structures

        self.individuals = {
            'I999': ind.Individual(
                'I999', 'Great Grandpa I001',
                birth_date='1890-11-11',
                birth_place='New York, USA',
                death_date='1965-02-15',
                death_place='New York, USA'
            ),
            'I001': ind.Individual(
                'I001', 'Grandpa I001',
                birth_date='1920-01-01',
                birth_place='New York, USA',
                death_date='1995-06-15',
                death_place='New York, USA'
            ),
            'I002': ind.Individual(
                'I002', 'Grandma I002',
                birth_date='1925-02-14',
                birth_place='Boston, USA',
                death_date='2000-09-21'
            ),
            'I003': ind.Individual(
                'I003', 'Son I001',
                birth_date='1950-05-20',
                birth_place='Chicago, USA'
            ),
            'I004': ind.Individual(
                'I004', 'Daughter I001',
                birth_date='1952-07-10',
                birth_place='Los Angeles, USA'
            ),
            'I005': ind.Individual(
                'I005', 'Son\'s Wife I005',
                birth_date='1955-11-02',
                birth_place='San Francisco, USA'
            ),
            'I006': ind.Individual(
                'I006', 'Grandson I001',
                birth_date='1980-03-15',
                birth_place='Seattle, USA'
            ),
            'I007': ind.Individual(
                'I007', 'Daughter\'s Husband I007',
                birth_date='1949-09-30',
                birth_place='Denver, USA'
            ),
            'I008': ind.Individual(
                'I008', 'Grandson, Uncle and Brother I007',
                birth_date='1985-04-25'
            ),
            'I009': ind.Individual(
                'I009', 'Granddaughter, Stepdaughter and Sister I007',
                birth_date='1987-08-17',
                birth_place='Austin, USA'
            ),
            'I010': ind.Individual(
                'I010', 'Granddaughter\'s Husband and Stepdad I010',
                birth_date='1975-12-01',
                birth_place='Phoenix, USA',
                death_date='2050-01-01',
                death_place='Phoenix, USA'
            ),
            'I011': ind.Individual(
                'I011', 'Great-grandson I010',
                birth_date='2010-02-28',
                birth_place='Dallas, USA'
            ),
            'I012': ind.Individual(
                'I012', 'Neighbor I012'
            ),
            'I013': ind.Individual(
                'I013', 'Great-grandson\'s Wife I013',
                birth_date='2012-07-14',
                birth_place='Miami, USA'
            ),
            'I014': ind.Individual(
                'I014', 'Husband I010\'s Wife I014',
                birth_date='1978-06-22',
                birth_place='Orlando, USA'
            ),
            'I015': ind.Individual(
                'I015', 'Circa Great-grand and Stepson I010',
                birth_date='2040-03-15',
                birth_place='Phoenix, USA'
            )
        }

        self.families = {
            'F999': f.Family('F999', 'I999', 'Great Grandpa I001', None, None, '1 JAN 1920', [self.individuals['I001']]),
            'F001': f.Family('F001', 'I001', 'Grandpa I001', 'I002', 'Grandma I002', '1 JAN 1950', [self.individuals['I003'], self.individuals['I004']]),
            'F002': f.Family('F002', 'I003', 'Son I001', 'I005', 'Son\'s Wife I005', '10 JUN 1980', [self.individuals['I006']]),
            'F003': f.Family('F003', 'I004', 'Daughter I001', 'I007', 'Daughter\'s Husband I007', '15 SEP 1985', [self.individuals['I008'], self.individuals['I009']]),
            'F004': f.Family('F004', 'I009', 'Granddaughter I007', 'I010', 'Granddaughter\'s Husband I010', '20 DEC 2015', [self.individuals['I011']]),
            'F005': f.Family('F005', 'I011', 'Great-grandson I010', 'I013', 'Great-grandson\'s Wife I013', '10 FEB 2040', []),
            'F006': f.Family('F006', 'I010', 'Granddaughter\'s Husband I010', 'I014', 'Wife to Husband I010 I014', '5 MAR 2020', [self.individuals['I015']])
        }

        self.relationships = [
            {'Source': 'I999', 'Target': 'I001', 'Relationship': 'parent-child'},
            {'Source': 'I001', 'Target': 'I003', 'Relationship': 'parent-child'},
            {'Source': 'I002', 'Target': 'I003', 'Relationship': 'parent-child'},
            {'Source': 'I001', 'Target': 'I004', 'Relationship': 'parent-child'},
            {'Source': 'I002', 'Target': 'I004', 'Relationship': 'parent-child'},
            {'Source': 'I003', 'Target': 'I006', 'Relationship': 'parent-child'},
            {'Source': 'I005', 'Target': 'I006', 'Relationship': 'parent-child'},
            {'Source': 'I004', 'Target': 'I008', 'Relationship': 'parent-child'},
            {'Source': 'I007', 'Target': 'I008', 'Relationship': 'parent-child'},
            {'Source': 'I004', 'Target': 'I009', 'Relationship': 'parent-child'},
            {'Source': 'I007', 'Target': 'I009', 'Relationship': 'parent-child'},
            {'Source': 'I009', 'Target': 'I011', 'Relationship': 'parent-child'},
            {'Source': 'I010', 'Target': 'I011', 'Relationship': 'parent-child'},
            {'Source': 'I011', 'Target': 'I015', 'Relationship': 'parent-child'},
            {'Source': 'I014', 'Target': 'I015', 'Relationship': 'parent-child'},
            {'Source': 'I010', 'Target': 'I015', 'Relationship': 'parent-child'},
            {'Source': 'I001', 'Target': 'I002', 'Relationship': 'spouse'},
            {'Source': 'I002', 'Target': 'I001', 'Relationship': 'spouse'},
            {'Source': 'I003', 'Target': 'I005', 'Relationship': 'spouse'},
            {'Source': 'I005', 'Target': 'I003', 'Relationship': 'spouse'},
            {'Source': 'I004', 'Target': 'I007', 'Relationship': 'spouse'},
            {'Source': 'I007', 'Target': 'I004', 'Relationship': 'spouse'},
            {'Source': 'I009', 'Target': 'I010', 'Relationship': 'spouse'},
            {'Source': 'I010', 'Target': 'I009', 'Relationship': 'spouse'},
            {'Source': 'I011', 'Target': 'I013', 'Relationship': 'spouse'},
            {'Source': 'I013', 'Target': 'I011', 'Relationship': 'spouse'},
            {'Source': 'I010', 'Target': 'I014', 'Relationship': 'spouse'},
            {'Source': 'I014', 'Target': 'I010', 'Relationship': 'spouse'},
            {'Source': 'I003', 'Target': 'I004', 'Relationship': 'sibling'},
            {'Source': 'I004', 'Target': 'I003', 'Relationship': 'sibling'},
            {'Source': 'I008', 'Target': 'I009', 'Relationship': 'sibling'},
            {'Source': 'I009', 'Target': 'I008', 'Relationship': 'sibling'},
            {'Source': 'I010', 'Target': 'I008', 'Relationship': 'step-parent'},
            {'Source': 'I010', 'Target': 'I009', 'Relationship': 'step-parent'},
            {'Source': 'I014', 'Target': 'I011', 'Relationship': 'step-parent'},
            {'Source': 'I014', 'Target': 'I008', 'Relationship': 'step-parent'},
            {'Source': 'I014', 'Target': 'I009', 'Relationship': 'step-parent'}
        ]

        data = FamilyTreeData()
        data._load_from_objs(self.individuals, self.families, self.relationships)
        self.manager = rm.RelationshipManager(data)

    def test_parent_child_relationships(self):
        parent_child = [rel for rel in self.relationships if rel['Source'] == 'I001' and rel['Target'] == 'I003' and rel['Relationship'] == 'parent-child']
        self.assertTrue("Grandpa I001 (I001) should be a parent of Son I001 (I003)", parent_child)

    def test_is_parent(self):
        self.assertTrue(self.manager.is_parent('I003', 'I001'), "Grandpa I001 (I001) should be a parent of Son I001 (I003)")
        self.assertFalse(self.manager.is_parent('I001', 'I003'), "Son I001 (I003) should not be a parent of Grandpa I001 (I001)")

    def test_get_parents_two(self):
        parents = self.manager.get_parents('I003')
        self.assertTrue('I001' in parents, "Son I001 (I003) should have Grandpa I001 (I001) in parents")

    def test_get_parents_one(self):
        parents = self.manager.get_parents('I001')
        self.assertTrue('I999' in parents, "Grandpa I001 (I001) should have Great Grandpa I001 (I999) in parents ({parents})")
        self.assertTrue(None in parents, "Grandpa I001 (I001) should have blank entry in parents ({parents})")

    def test_get_parents_none(self):
        parents = self.manager.get_parents('I999')
        self.assertTrue([] == parents, "Great Grandpa I001 (I999) has no parents in tree")

    def test_spousal_relationship(self):
        spouses = [rel for rel in self.relationships if rel['Source'] == 'I001' and rel['Target'] == 'I002' and rel['Relationship'] == 'spouse']
        self.assertTrue("Grandpa I001 (I001) should be a spouse of Grandma I002 (I002)", spouses)

    def test_is_spouse(self):
        self.assertTrue(self.manager.is_spouse('I001', 'I002'), "Grandpa I001 (I001) should be a spouse of Grandma I002 (I002)")
        self.assertFalse(self.manager.is_spouse('I001', 'I003'), "Grandpa I001 (I001) should not be a spouse of Son I001 (I003)")

    def test_get_children_two(self):
        children = self.manager.get_children('I001')
        self.assertTrue('I003' in children, "Grandpa I001 (I001) should have Son I001 (I003) in children")
        self.assertTrue('I004' in children, "Grandpa I001 (I001) should have Daughter I001 (I004) in children")

    def test_get_children_zero(self):
        children = self.manager.get_children('I015')
        self.assertEqual([], children, "I015 should have no children")

    def test_sibling_relationship(self):
        siblings = [rel for rel in self.relationships if rel['Source'] == 'I003' and rel['Target'] == 'I004' and rel['Relationship'] == 'sibling']
        self.assertTrue("Son I001 (I003) should be a sibling of Daughter I001 (I004)", siblings)

    def test_step_parent_relationship(self):
        step_parent = [rel for rel in self.relationships if rel['Source'] == 'I010' and rel['Target'] == 'I008' and rel['Relationship'] == 'step-parent']
        self.assertTrue("Granddaughter's Husband I010 (I010) should be a step-parent of Grandson I007 (I008)", step_parent)

    def test_multiple_marriages(self):
        spouses = [rel for rel in self.relationships if rel['Source'] == 'I010' and rel['Relationship'] == 'spouse']
        self.assertTrue("Granddaughter's Husband I010 (I010) should have multiple spouses", len(spouses) > 1)

    def test_multiple_children(self):
        children = [rel for rel in self.relationships if rel['Source'] == 'I004' and rel['Relationship'] == 'parent-child']
        self.assertTrue("Daughter I001 (I004) should have multiple children", len(children) > 1)

    @pytest.mark.xfail
    def test_multiple_siblings(self):
        siblings = [rel for rel in self.relationships if rel['Source'] == 'I008' and rel['Relationship'] == 'sibling']
        self.assertEqual("Grandson I007 (I008) should not have multiple siblings", 1, len(siblings))

    def test_multiple_step_parents(self):
        step_parents = [rel for rel in self.relationships if rel['Target'] == 'I008' and rel['Relationship'] == 'step-parent']
        self.assertTrue("Grandson I007 (I008) should have multiple step-parents", len(step_parents) > 1)

    @pytest.mark.xfail
    def test_multiple_families(self):
        families = [family for family in self.families.values() if 'I008' in [child.id for child in family.children]]
        self.assertEqual("Grandson I007 (I008) should not have multiple families", 1, len(families))

    def test_multiple_spouses(self):
        spouses = [rel for rel in self.relationships if rel['Source'] == 'I010' and rel['Relationship'] == 'spouse']
        self.assertTrue("Granddaughter's Husband I010 (I010) should have multiple spouses", len(spouses) > 1)

    def test_multiple_parents(self):
        parents = [rel for rel in self.relationships if rel['Target'] == 'I008' and rel['Relationship'] == 'parent-child']
        self.assertTrue("Grandson I007 (I008) should have multiple parents", len(parents) > 1)

    def test_multiple_children_in_family(self):
        f003_family = self.families['F003']
        self.assertTrue("Family F003 should have multiple children", len(f003_family.children) > 1)

    def test_relationship_parent_child_one_per_pair(self):
        parent_child_rels = [(rel['Source'], rel['Target']) for rel in self.relationships if rel['Relationship'] == 'parent-child']
        self.assertEqual(len(set(parent_child_rels)), len(parent_child_rels), f"There should be only one parent-child relationship between any two individuals.\n"
                         f"Extra relationship: {[relationship for relationship in parent_child_rels if relationship not in set(parent_child_rels)]}")

    def test_relationship_sibling_two_way(self):
        sibling_rels = [(rel['Source'], rel['Target']) for rel in self.relationships if rel['Relationship'] == 'sibling']
        unvisited_sibling_rels = sibling_rels.copy()
        while len(unvisited_sibling_rels) > 0:
            source, target = unvisited_sibling_rels.pop()
            if (target, source) in unvisited_sibling_rels:
                unvisited_sibling_rels.remove((target, source))
            else:
                self.fail(f"Missing reciprocal sibling relationship for ({source}, {target})")

    def test_get_ancestors_three(self):
        self.assertEqual({'I001', 'I999', 'I002'}, self.manager.get_ancestors('I003', depth=2))

    def test_get_ancestors_zero(self):
        self.assertEqual(set(), self.manager.get_ancestors('I999', depth=2))

    def test_get_descendents_one(self):
        self.assertEqual({'I006'}, self.manager.get_descendents('I003', depth=2))

    def test_get_descendents_depth_10(self):
        self.assertEqual({'I003', 'I004', 'I006', 'I008', 'I009', 'I011'}, self.manager.get_descendents('I001', depth=10))

    @pytest.mark.xfail
    def test_find_common_ancestor(self):
        pass

    @pytest.mark.xfail
    def test_calculate_generational_distance(self):
        # Valid ancestor relationship
        # Dad
        self.assertEqual(1, self.manager.calculate_generational_distance('I1', 'I3'))
        # self.assertEqual(None, self.manager.calculate_generational_distance('I1', 'I4'))

        # No ancestor relationship
        # Spouse
        self.assertEqual(None, self.manager.calculate_generational_distance('I1', 'I4'))
        # self.assertEqual(float('inf'), self.manager.calculate_generational_distance('I1', 'Unknown'))