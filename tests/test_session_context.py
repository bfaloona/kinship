import unittest
from session_context import SessionContext


class TestSessionContext(unittest.TestCase):

    def setUp(self):
        # Sample individuals data
        self.individuals_data = {
            "id001": "John Smith",
            "id002": "Jane Doe",
            "id003": "Robert Johnson",
        }
        self.context = SessionContext(self.individuals_data)

    def test_add_alias(self):
        self.context.add_alias("Johnny", "id001")
        self.assertEqual(self.context.lookup_id_by_alias("Johnny"), "id001")

    def test_lookup_id_by_alias(self):
        self.context.add_alias("Jane", "id002")
        result = self.context.lookup_id_by_alias("Jane")
        self.assertEqual(result, "id002")

    def test_add_active_player(self):
        self.context.add_active_player("id001")
        self.assertTrue(self.context.is_active_player("id001"))

    def test_remove_active_player(self):
        self.context.add_active_player("id001")
        self.context.remove_active_player("id001")
        self.assertFalse(self.context.is_active_player("id001"))

    def test_get_active_players(self):
        self.context.add_active_player("id001")
        self.context.add_active_player("id002")
        active_players = self.context.get_active_players()
        self.assertListEqual(active_players, ["id001", "id002"])

    def test_resolve_alias_direct_match(self):
        self.context.add_alias("Johnny", "id001")
        result = self.context.resolve_alias("Johnny")
        self.assertEqual(result, "id001")

    def test_resolve_alias_fuzzy_match(self):
        self.context.add_alias("Johnny", "id001")
        result = self.context.resolve_alias("John Smith")
        self.assertEqual(result, "id001")

    def test_validate_alias_conflicts(self):
        self.context.add_alias("Johnny", "id001")
        self.context.add_alias("JohnnyBoy", "id001")
        self.context.validate_alias_conflicts()
        # Check manually in the logs for conflict warning

    def test_get_individual_by_id(self):
        individual = self.context.get_individual_by_id("id001")
        self.assertEqual(individual, "John Smith")

    def test_add_individual(self):
        self.context.add_individual("Bobby", "Bob Brown", "id004")
        self.assertEqual(self.context.get_individual_by_id("id004"), "Bob Brown")
        self.assertEqual(self.context.lookup_id_by_alias("Bobby"), "id004")

    def test_display_active_players(self):
        self.context.add_active_player("id001")
        self.context.add_active_player("id002")
        self.context.display_active_players()  # Check output manually for player details

