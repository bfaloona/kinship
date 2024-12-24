import individual

class SessionContext:
    """
        Tracks the mapping of human-friendly aliases to
        authoritative unique IDs for Individual references,
        plus a list of currently active (verified) individuals in a 'game'.
        """

    def __init__(self):
        # Maps aliases (e.g. 'Bob', 'Bobby') to unique IDs (e.g. 'user001')
        self.alias_map = {}

        # Set of IDs representing the currently active (verified) individuals
        self.active_players = set()

    def add_alias(self, alias: str, individual_id: str):
        """
        Adds or updates a mapping between an alias and a unique ID.
        """
        self.alias_map[alias.lower()] = individual_id

    def lookup_id_by_alias(self, alias: str) -> str:
        """
        Returns the unique ID for a given alias if it exists, else None.
        """
        return self.alias_map.get(alias.lower())

    def add_active_player(self, individual_id: str):
        """
        Marks an individual as 'active' (in a current game, for instance).
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
        Checks if an individual is in the current active set.
        """
        return individual_id in self.active_players

    def get_active_players(self):
        """
        Returns a list of currently active player IDs.
        """
        return list(self.active_players)