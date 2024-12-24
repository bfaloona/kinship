from fuzzywuzzy import process

class SessionContext:
    """
    Tracks the mapping of human-friendly aliases to
    authoritative unique IDs for Individual references,
    plus a list of currently active (verified) individuals in a 'game'.
    """

    def __init__(self, individuals_data):
        """
        Initialize SessionContext with a dataset of individuals.
        :param individuals_data: A dictionary mapping individual IDs to full names.
        """
        self.alias_map = {}  # Maps aliases (e.g. 'Bob', 'Bobby') to unique IDs
        self.active_players = set()  # IDs of active individuals in a game
        self.individuals_data = individuals_data  # All known individuals in dataset

    def add_alias(self, alias: str, individual_id: str):
        """
        Adds or updates a mapping between an alias and a unique ID.
        """
        self.alias_map[alias.lower()] = individual_id

    def lookup_id_by_alias(self, alias: str):
        """
        Returns the unique ID for a given alias if it exists, else None.
        """
        return self.alias_map.get(alias.lower())

    def add_active_player(self, individual_id: str):
        """
        Marks an individual as 'active' in a game.
        """
        self.active_players.add(individual_id)

    def remove_active_player(self, individual_id: str):
        """
        Removes an individual from the active set.
        """
        if individual_id in self.active_players:
            self.active_players.remove(individual_id)

    def is_active_player(self, individual_id: str) -> bool:
        """
        Checks if an individual is an active player in the current game.
        """
        return individual_id in self.active_players

    def get_active_players(self):
        """
        Returns a list of currently active player IDs.
        """
        return list(self.active_players)

    def resolve_alias(self, alias: str):
        """
        Resolves an alias to an individual ID using fuzzy matching.
        Confirms with the user before adding new mappings.
        """
        # Step 1: Check if alias exists directly
        individual_id = self.lookup_id_by_alias(alias)
        if individual_id:
            return individual_id

        # Step 2: Fuzzy match against known individuals
        matches = process.extract(alias, self.individuals_data.values(), limit=3)
        suggestions = [match for match in matches if match[1] > 75]  # Confidence threshold

        if not suggestions:
            return None

        # Step 3: Ask user to confirm closest match or add new alias
        print(f"Did you mean one of these? {', '.join([match[0] for match in suggestions])}")
        selected = input("Type the exact name or 'none' to reject: ").strip().lower()

        if selected == 'none':
            print("No match found.")
            return None

        for name, confidence in suggestions:
            if name.lower() == selected:
                # Find the corresponding ID
                for id, full_name in self.individuals_data.items():
                    if full_name.lower() == name.lower():
                        self.add_alias(alias, id)
                        return id

        # If user confirms none, return None
        print("Could not resolve alias.")
        return None

    def validate_alias_conflicts(self):
        """
        Checks for conflicts or near conflicts between aliases.
        Re-validates mappings to ensure no duplication or errors.
        """
        reversed_map = {}
        for alias, id in self.alias_map.items():
            if id not in reversed_map:
                reversed_map[id] = []
            reversed_map[id].append(alias)

        for id, aliases in reversed_map.items():
            if len(aliases) > 1:
                print(f"Warning: Multiple aliases for ID {id}: {', '.join(aliases)}")

    def get_individual_by_id(self, individual_id: str):
        """
        Retrieves individual details by ID.
        """
        return self.individuals_data.get(individual_id)

    def add_individual(self, alias: str, full_name: str, individual_id: str):
        """
        Add a new individual and map their alias.
        """
        if individual_id in self.individuals_data:
            print(f"Individual ID {individual_id} already exists.")
            return
        self.individuals_data[individual_id] = full_name
        self.add_alias(alias, individual_id)

    def display_active_players(self):
        """
        Prints details of active players.
        """
        for player_id in self.get_active_players():
            print(self.get_individual_by_id(player_id))
