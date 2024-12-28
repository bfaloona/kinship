import unittest
from kinship.session_context import SessionContext

class TestSessionContext(unittest.TestCase):

    def setUp(self):
        # Sample individuals data
        self.individuals_data = {
            "I0001": "John Smith",
            "I0002": "Jane Doe",
            "I0003": "Robert Johnson",
        }
        self.context = SessionContext(self.individuals_data)

    def test_resolve_alias_direct_match(self):
        self.context.add_alias("Johnny", "I0001")
        result = self.context.resolve_alias("Johnny")
        self.assertEqual(result["resolved_id"], "I0001")
        self.assertEqual(result["status"], "resolved_directly")

    def test_resolve_alias_fuzzy_match(self):
        result = self.context.resolve_alias("John", confidence_threshold=70)
        self.assertEqual(result["status"], "suggestions_found")
        self.assertTrue(any(s["name"] == "John Smith" for s in result["suggestions"]))

    def test_resolve_alias_no_match(self):
        result = self.context.resolve_alias("Nonexistent Name", confidence_threshold=70)
        self.assertEqual(result["status"], "no_matches")

    def test_list_potential_matches(self):
        matches = self.context.list_potential_matches("Jane", confidence_threshold=50)
        self.assertTrue(any(m["name"].lower() == "jane doe" for m in matches))

    def test_validate_alias_conflicts(self):
        self.context.add_alias("Johnny", "I0001")
        self.context.add_alias("JohnnyBoy", "I0001")
        conflicts = self.context.validate_alias_conflicts()
        self.assertEqual(1, len(conflicts))
        self.assertEqual("I0001", conflicts[0]["individual_id"])
        self.assertCountEqual(conflicts[0]["aliases"], ["johnny", "johnnyboy"])

    def test_add_alias(self):
        self.context.add_alias("Johnny", "I0001")
        self.assertEqual(self.context.lookup_id_by_alias("Johnny"), "I0001")

    def test_lookup_id_by_alias(self):
        self.context.add_alias("Jane", "I0002")
        result = self.context.lookup_id_by_alias("Jane")
        self.assertEqual(result, "I0002")

    def test_add_active_player(self):
        self.context.add_active_player("I0001")
        self.assertTrue(self.context.is_active_player("I0001"))

    def test_remove_active_player(self):
        self.context.add_active_player("I0001")
        self.context.remove_active_player("I0001")
        self.assertFalse(self.context.is_active_player("I0001"))

    def test_get_active_players(self):
        self.context.add_active_player("I0001")
        self.context.add_active_player("I0002")
        active_players = self.context.get_active_players()
        self.assertCountEqual(active_players, ["I0001", "I0002"])

    def test_get_individual_by_id(self):
        individual = self.context.get_individual_by_id("I0001")
        self.assertEqual(individual, "John Smith")

    def test_add_individual(self):
        self.context.add_individual("Bobby", "Bob Brown", "id004")
        self.assertEqual(self.context.get_individual_by_id("id004"), "bob brown")
        self.assertEqual(self.context.lookup_id_by_alias("Bobby"), "id004")

    def test_resolve_alias_auto_add(self):
        result = self.context.resolve_alias("John S")
        self.assertEqual("resolved_and_added", result["status"])
        self.assertIn("john s", self.context.alias_map)

    def test_resolve_alias_auto_add_high_con(self):
        result = self.context.resolve_alias("John Smit", confidence_threshold=90, auto_add=True)
        self.assertEqual("resolved_and_added", result["status"])
        self.assertIn("john smit", self.context.alias_map)

    def test_resolve_alias_auto_add_false(self):
        result = self.context.resolve_alias("J", confidence_threshold=60, auto_add=False)
        self.assertEqual(result["status"], "suggestions_found")
        self.assertNotIn("j", self.context.alias_map)

    def test_display_active_players(self):
        self.context.add_active_player("I0001")
        self.context.add_active_player("I0002")
        self.assertTrue("John Smith" in self.context.display_active_players())
        self.assertTrue("Jane Doe" in self.context.display_active_players())

if __name__ == "__main__":
    unittest.main()
