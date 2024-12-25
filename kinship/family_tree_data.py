
from archive.poc_gpt import calculate_relationship
from kinship.individual import Individual
from kinship.family import Family
from kinship.gedcom_parser import GedcomParser


class FamilyTreeData:
    """
    A robust class for managing family tree data with support for loading, querying, and testing.
    The data is read-only to ensure the source of truth (e.g., GEDCOM file) is preserved.
    """
    def __init__(self):
        self.individuals = {}  # Dictionary of individual_id -> individual details
        self.families = {}  # Dictionary of family_id -> family details
        self.relationships = []  # Dictionary of individual_id -> list of relationships

    def load_from_gedcom(self, gedcom_parser: GedcomParser):
        """
        Load data from a GEDCOM parser instance.
        """
        self.individuals = gedcom_parser.get_individuals()
        self.families = gedcom_parser.get_families()
        self.relationships = gedcom_parser.get_relationships()
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

    def load_families_from_csv(self, file_path):
        import csv

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                family_id = row['Family_ID']
                if family_id not in self.families:
                    self.families[family_id] = Family(
                        id=row['Family_ID'],
                        husband_id=row['Husband_ID'],
                        husband_name=row['Husband_Name'],
                        wife_id=row['Wife_ID'],
                        wife_name=row['Wife_Name'],
                        marr_date=row['Marriage_Date']
                    )
                self.families[family_id].children.append(row['Child_ID'])

    def load_individuals_from_csv(self, file_path):
        import csv
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                individual_id = row['Individual_ID']
                self.individuals[individual_id] = Individual(
                    id=row['Individual_ID'],
                    full_name=row['Individual_Name'],
                    birth_date=row['Birth_Date'],
                    birth_place=row['Birth_Place'],
                    death_date=row['Death_Date'],
                    death_place=row['Death_Place']
                )

    def load_relationships_from_csv(self, file_path):
        import csv
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            self.relationships = [row for row in reader]



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

    def check_data_integrity(self):
        """
        Validate data integrity.
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
