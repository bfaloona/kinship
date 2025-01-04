from kinship.individual import Individual
from kinship.family import Family


class FamilyTreeData:
    """
    A robust class for managing family tree data with support for loading, querying, and testing.
    The data is read-only to ensure the source of truth (e.g., GEDCOM file) is preserved.
    """
    def __init__(self):
        self.individuals = {}  # Dictionary of individual_id -> individual details
        self.families = {}  # Dictionary of family_id -> family details

    def load_from_processed_files(self, individuals_file, families_file):
        """
        Load data from pre-processed CSV files.
        """
        self.load_individuals_from_csv(individuals_file)
        self.load_families_from_csv(families_file)
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

    def calculate_generations(self):
        generations = {}

        # Initialize generations for individuals without parents
        for individual_id in self.individuals:
            generations[individual_id] = 0

        updated = True
        while updated:
            updated = False
            for family in self.families.values():
                for child_id in family.children:
                    for parent_id in [family.husband_id, family.wife_id]:
                        if parent_id and parent_id in generations:
                            new_gen = generations[parent_id] + 1
                            if child_id not in generations or generations[child_id] < new_gen:
                                generations[child_id] = new_gen
                                updated = True

        return generations

    def get_individual(self, individual_id) -> Individual:
        """
        Retrieve details of an individual by ID.
        """
        id = self.individuals.get(individual_id)
        if id is None:
            raise ValueError(f"Individual ID {individual_id} not found")
        else:
            return id

    def get_gender(self, individual_id) -> Individual:
        """
        Retrieve details of an individual by ID.
        """
        return self.individuals.get(individual_id).sex

    def get_family(self, family_id):
        """
        Retrieve details of a family by ID.
        """
        return self.families.get(family_id)

    def get_spouses(self, individual_id):
        """
        Retrieve the ID of all spouses of an individual.
        """
        spouses = []
        for family in self.families.values():
            if family.husband_id == individual_id:
                spouses.append(family.wife_id)
            if family.wife_id == individual_id:
                spouses.append(family.husband_id)
        return spouses

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

    def get_children(self, individual_id) -> set:
        """
        Retrieve IDs of children.
        """
        children = set()
        for family in self.families.values():
            if individual_id in [family.husband_id, family.wife_id]:
                children.update(family.children)
        return children

    def get_husband(self, individual_id):
        """
        Retrieve the ID of the father of an individual.
        """
        for family in self.families.values():
            if individual_id in family.children:
                return family.husband_id
        return None

    def get_wife(self, individual_id):
        """
        Retrieve the ID of the mother of an individual.
        """
        for family in self.families.values():
            if individual_id in family.children:
                return family.wife_id
        return None

    def get_siblings(self, individual_id) -> set:
        """
        Retrieve IDs of siblings.
        """
        siblings = set()
        for family in self.families.values():
            if individual_id in family.children:
                siblings.update(family.children)
                siblings.discard(individual_id)  # Remove the individual itself
        return siblings

    def get_all_siblings(self, individual_id) -> set:
        """
        Retrieve IDs of sibling from all families that include parents.
        """
        all_siblings = set()
        all_families = set()
        parents = self.get_parents(individual_id)
        for family in self.families.values():
            for parent in parents:
                if parent in family.get_parents():
                    all_families.add(family)
        for family in all_families:
            all_siblings.update(family.children)
            all_siblings.discard(individual_id)  # Remove the individual itself
        return all_siblings

    def verify_integrity(self):
        """
        Verify the integrity of the data.
        """
        # Check for orphaned individuals (not part of any family or relationships)
        unknown_individuals = set()
        for fam in self.families.values():
            family_members = [fam.husband_id, fam.wife_id]
            family_members.extend(fam.children)
            for ind in family_members:
                if ind not in self.individuals:
                    unknown_individuals.add(ind)
            if len(unknown_individuals) > 0:
                raise ValueError(f"Unknown individual detected: {unknown_individuals}")

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
            result = f"Family: {fam.id}\n{self.display(fam.husband_id)} + {self.display(fam.wife_id)} M:{fam.marr_date}\n{fam.children}\n"

        return result
