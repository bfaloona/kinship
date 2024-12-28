from fuzzywuzzy import process

class SessionContext:
    """
    Tracks the mapping of human-friendly aliases to
    authoritative unique IDs for Individual references,
    plus a list of currently active (verified) individuals in a 'game'.
    """

    def __init__(self, individuals_data):
        # Store individuals data in lowercase for efficient matching
        self.alias_map = {}  # Maps aliases (e.g. 'Bob', 'Bobby') to unique IDs
        self.active_players = set()  # IDs of active individuals in a game
        self.individuals_data = individuals_data  # Dict{id: Individual} of all known individuals
        self.conflict_log = []  # Tracks alias conflicts for GPT resolution

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

    def get_active_players(self) -> []:
        """
        Returns a list of currently active player IDs.
        """
        return list(self.active_players)

    def alias_matched(self, alias: str) -> bool:
        result = self.resolve_alias(alias)
        return result["status"] == "resolved_directly" or result["status"] == "resolved_and_added"

    def resolve_alias(self, alias: str, confidence_threshold: int = 80, auto_add: bool = True):
        """
        Resolves an alias to an individual ID using fuzzy matching.
        :param alias: The alias to resolve.
        :param confidence_threshold: Minimum confidence score for a match to be considered.
        :param auto_add: Whether to add the resolved alias to the alias_map.
        :return: A dictionary with resolved ID, suggestions, or a flag for no matches.
        """
        # Step 1: Check if alias exists directly
        individual_id = self.lookup_id_by_alias(alias)
        if individual_id:
            return {"resolved_id": individual_id, "status": "resolved_directly"}

        # Step 2: Fuzzy match against known individuals
        matches = process.extract(alias, self.individuals_data.values(), limit=5)
        suggestions = [{"name": match[0], "confidence": match[1]} for match in matches if
                       match[1] >= confidence_threshold]

        if suggestions:
            # Automatically add the best match if auto_add is enabled
            if len(suggestions) == 1:
                best_match = matches[0]
                if auto_add and best_match[1] >= confidence_threshold:
                    best_name = best_match[0]
                    matched_id = next((id for id, name in self.individuals_data.items() if name == best_name), None)
                    if matched_id:
                        self.add_alias(alias, matched_id)
                        return {"resolved_id": matched_id, "status": "resolved_and_added"}

            return {"suggestions": suggestions, "status": "suggestions_found"}
        else:
            return {"status": "no_matches"}

    def validate_alias_conflicts(self):
        """
        Checks for conflicts or near conflicts between aliases.
        :return: A list of conflicting alias mappings.
        """
        conflicts = []
        reverse_map = {}

        for alias, individual_id in self.alias_map.items():
            if individual_id not in reverse_map:
                reverse_map[individual_id] = []
            reverse_map[individual_id].append(alias)

        for individual_id, aliases in reverse_map.items():
            if len(aliases) > 1:
                conflicts.append({"individual_id": individual_id, "aliases": aliases})

        self.conflict_log = conflicts
        return conflicts

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
        self.individuals_data[individual_id] = full_name.lower()
        self.add_alias(alias, individual_id)

    def display_active_players(self) -> str:
        """
        Prints details of active players.
        """
        output = ""
        for player_id in self.get_active_players():
            output = f"{output}{self.get_individual_by_id(player_id)}\n"
        return output

    def list_potential_matches(self, alias: str, confidence_threshold=60):
        """
        Lists potential matches for a given alias using fuzzy matching.
        :param alias: The alias to match.
        :param confidence_threshold: Minimum confidence score for matches.
        :return: A list of potential matches with confidence scores.
        """
        matches = process.extract(alias.lower(), self.individuals_data.values(), limit=10)
        return [
            {"name": match[0], "confidence": match[1]}
            for match in matches if match[1] >= confidence_threshold
        ]

    def add_alias_with_confirmation(self, alias: str, individual_id: str):
        """
        Adds an alias to an individual with confirmation to avoid conflicts.
        :param alias: The alias to add.
        :param individual_id: The individual ID to map the alias to.
        """
        existing_id = self.lookup_id_by_alias(alias)
        if existing_id and existing_id != individual_id:
            print(f"Conflict: Alias '{alias}' is already mapped to ID '{existing_id}'.")
            return
        self.add_alias(alias, individual_id)
