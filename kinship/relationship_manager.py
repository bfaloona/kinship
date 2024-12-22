class RelationshipManager:
    def __init__(self, individuals):
        # Store individuals in a dictionary for quick access
        self.individuals = individuals

    # Read-only methods for querying relationships
    def is_parent(self, parent_id, child_id):
        """Check if an individual is a parent of another."""
        return child_id in self.individuals[parent_id].children

    def is_sibling(self, individual1_id, individual2_id):
        """Check if two individuals share at least one parent."""
        parents1 = self.individuals[individual1_id].parents
        parents2 = self.individuals[individual2_id].parents
        return bool(set(parents1) & set(parents2))

    def get_ancestors(self, individual_id, depth=1):
        """Retrieve ancestors up to a given depth."""
        ancestors = set()
        current_generation = {individual_id}
        for _ in range(depth):
            next_generation = set()
            for person_id in current_generation:
                next_generation.update(self.individuals[person_id].parents)
            ancestors.update(next_generation)
            current_generation = next_generation
        return ancestors

    def describe_relationship(self, person1_id, person2_id):
        """Describe the relationship between two individuals."""
        if self.is_parent(person1_id, person2_id):
            return "parent"
        if self.is_parent(person2_id, person1_id):
            return "child"
        if self.is_sibling(person1_id, person2_id):
            return "sibling"
        if person1_id in self.get_ancestors(person2_id, depth=2):
            return "grandparent"
        if person2_id in self.get_ancestors(person1_id, depth=2):
            return "grandchild"
        if self.individuals[person1_id].spouse == person2_id:
            return "spouse"
        return "unknown relationship"
