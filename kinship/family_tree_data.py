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

    def load_from_gedcom(self, gedcom_parser: GedcomParser):
        """
        Load data from a GEDCOM parser instance.
        """
        self.individuals = gedcom_parser.get_individuals()
        self.families = gedcom_parser.get_families()
        return self

    def load_from_processed_files(self, individuals_file, families_file):
        """
        Load data from pre-processed CSV files.
        """
        self.individuals = self._load_csv(individuals_file, mode="hash_with_id")
        self.families = self._load_csv(families_file, mode="hash_with_id")
        return self

    def _load_from_objs(self, individuals, families):
        """
        Load data from pre-processed CSV files.
        """
        self.individuals = individuals
        self.families = families
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
                    sex=row['Sex'],
                    birth_date=row['Birth_Date'],
                    birth_place=row['Birth_Place'],
                    death_date=row['Death_Date'],
                    death_place=row['Death_Place']
                )

    def get_individual(self, individual_id) -> Individual:
        """
        Retrieve details of an individual by ID.
        """
        return self.individuals.get(individual_id)

    def get_family(self, family_id):
        """
        Retrieve details of a family by ID.
        """
        return self.families.get(family_id)

    def get_parents(self, individual_id) -> set:
        """
        Retrieve IDs of parents.
        """
        parents = set()
        for family in self.families.values():
            if individual_id in family.children:
                if family.husband_id:
                    parents.add(family.husband_id)
                if family.wife_id:
                    parents.add(family.wife_id)
        return parents


    def verify_integrity(self):
        """
        Verify the integrity of the data.
        """
        # Check for orphaned individuals (not part of any family or relationships)
        orphaned_individuals = [
            ind for ind in self.individuals.keys()
            if not any(ind in fam for fam in self.families.values())
        ]
        if orphaned_individuals:
            raise ValueError(f"Orphaned individuals detected: {orphaned_individuals}")

    def __delattr__(self, item):
        """
        Prevent deletion of attributes to ensure data integrity.
        """
        raise AttributeError("FamilyTreeData attributes cannot be deleted.")


    def display(self, content) -> str:
        """Pretty Print content depending on the type"""
        from kinship.family import Family
        from kinship.individual import Individual

        result = content
        if content is None:
            result = "None"

        elif isinstance(content, list):
            if not content:
                result = "list[]"
            elif isinstance(content[0], Individual) or \
                    isinstance(content[0], Family):
                result = "\n".join([self.display(ind) for ind in content])

        elif isinstance(content, set):
            if not content:
                result = "set()"
            else:
                result = "\n".join([self.display(item) for item in content])

        elif isinstance(content, dict):
            if not content:
                result = "dict{}"
            else:
                result = "\n".join([f"{k}: {self.display(v)}" for k, v in content.items()])

        elif isinstance(content, str):
            if content in self.individuals:
                result = self.display(self.individuals[content])
            else:
                result = content

        elif isinstance(content, Individual):
            result = f"{content.full_name} ({content.id})"

        elif isinstance(content, Family):
            fam = content
            result = f"Family: {fam.id}\n{self.display(fam.husband_id)} + {self.display(fam.wife_id)} M:{fam.marr_date}\n{[self.display(child_id) + " " for child_id in fam.children]}\n"

        return result
