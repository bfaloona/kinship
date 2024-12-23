
from archive.poc_gpt import calculate_relationship

class FamilyTreeData:
    """
    A robust class for managing family tree data with support for loading, querying, and testing.
    The data is read-only to ensure the source of truth (e.g., GEDCOM file) is preserved.
    """
    def __init__(self):
        self.individuals = {}  # Dictionary of individual_id -> individual details
        self.families = {}  # Dictionary of family_id -> family details
        self.relationships = []  # Dictionary of individual_id -> list of relationships

    def load_from_gedcom(self, gedcom_parser):
        """
        Load data from a GEDCOM parser instance.
        """
        self.individuals = gedcom_parser.parse_individuals()
        self.families = gedcom_parser.parse_families()
        self.relationships = gedcom_parser.parse_relationships()
        return self

    def load_from_processed_files(self, individuals_file, families_file, relationships_file):
        """
        Load data from pre-processed CSV files.
        """
        self.individuals = self._load_csv(individuals_file, mode="hash_with_id")
        self.families = self._load_csv(families_file, mode="hash_with_id")
        self.relationships = self._load_csv(relationships_file, mode="hash_per_row")
        return self

    def _load_from_objs(self, individuals, families, relationships):
        """
        Load data from pre-processed CSV files.
        """
        self.individuals = individuals
        self.families = families
        self.relationships = relationships
        return self

    @staticmethod
    def _load_csv(file_path, mode="hash_with_id"):
        """
        Helper method to load CSV data into a dictionary or list based on the mode.

        :param file_path: Path to the CSV file.
        :param mode: "hash_with_id" (id -> hash) or "hash_per_row" (list of hashes).
        """
        import csv

        if mode not in {"hash_with_id", "hash_per_row"}:
            raise ValueError("Invalid mode. Choose 'hash_with_id' or 'hash_per_row'.")

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            if mode == "hash_with_id":
                return {row['id']: row for row in reader}
            elif mode == "hash_per_row":
                return [row for row in reader]


    def get_individual(self, individual_id):
        """
        Retrieve details of an individual by ID.
        """
        return self.individuals.get(individual_id)

    def get_family(self, family_id):
        """
        Retrieve details of a family by ID.
        """
        return self.families.get(family_id)

    def get_relationships(self, individual_id):
        """
        Retrieve the relationships of an individual by ID.
        """
        return self.relationships.get(individual_id, [])

    def get_relationship(self, individual_id1, individual_id2):
        """
        Retrieve the relationship between two individuals.
        """
        try:
            return individual_id2 in self.get_relationships(individual_id1)
        except KeyError:
            return calculate_relationship(individual_id1, individual_id2)


    def verify_integrity(self):
        """
        Verify the integrity of the data.
        """
        # Check for orphaned individuals (not part of any family or relationships)
        orphaned_individuals = [
            ind for ind in self.individuals.keys()
            if ind not in self.relationships and not any(ind in fam for fam in self.families.values())
        ]
        if orphaned_individuals:
            raise ValueError(f"Orphaned individuals detected: {orphaned_individuals}")

    def validate_data(self):
        """
        Validate the data for unit and integration testing.
        """
        # Example: Check if every relationship points to a valid individual
        for individual, relations in self.relationships.items():
            for related_individual in relations:
                if related_individual not in self.individuals:
                    raise ValueError(f"Invalid relationship: {individual} -> {related_individual}")

    # def __setattr__(self, key, value):
    #     """
    #     Prevent modification of attributes to ensure data integrity.
    #     """
    #     if hasattr(self, key):
    #         if not key.startswith("_"):
    #             raise AttributeError("FamilyTreeData is read-only. Modifications are not allowed.")
    #     super().__setattr__(key, value)

    def __delattr__(self, item):
        """
        Prevent deletion of attributes to ensure data integrity.
        """
        raise AttributeError("FamilyTreeData attributes cannot be deleted.")
