from typing import Final
from collections import defaultdict

from kinship.gedcom_parser import create_parent_to_children, create_parent_to_step_children
from kinship.individual import Individual
from kinship.family import Family
from kinship.family_tree_data import FamilyTreeData


class RelationshipManager:

    def __init__(self, data: FamilyTreeData):
        """Store data in read-only format."""
        self.individuals: Final = data.individuals
        self.families: Final = data.families
        self.relationships: Final = data.relationships
        self.child_to_parents = {}
        self.parent_to_children = {}
        self.parent_to_step_children = {}
        self.spouse_relationships = {}
        self.sibling_relationships = {}

        self.validate_family_tree_data()

        for fam in self.families.values():
            for child in fam.children:
                self.child_to_parents[child.id] = {fam.husband_id, fam.wife_id}
        self.parent_to_children = create_parent_to_children(self.families)
        self.parent_to_step_children = create_parent_to_step_children(self.families, self.parent_to_children)
        self.generate_spouse_and_sibling_lookups()

    def validate_family_tree_data(self):
        # Family data validation
        for family in self.families.values():
            if not family.husband_id or family.husband_id == "Unknown":
                raise ValueError ("Invalid data: missing ID")
            if not family.wife_id or family.wife_id == "Unknown":
                raise ValueError ("Invalid data: missing ID")

    def individual_exists(self, individual_id):
        """Check if the individual ID is valid."""
        if individual_id not in self.individuals:
            print(f"Individual ID {individual_id} not found.")
            return False
        return True

    def generate_spouse_and_sibling_lookups(self):
        """
        Generate spouse and sibling lookups from the relationships data.
        """

        # Build spouse relationship - each spouse pair is bidirectional
        for rel in [rel for rel in self.relationships if rel['Relationship'] == 'spouse']:
            self.spouse_relationships[rel['Source']] = rel['Target']
            self.spouse_relationships[rel['Target']] = rel['Source']

        # Build sibling relationships - each sibling pair is bidirectional
        for rel in [rel for rel in self.relationships if rel['Relationship'] == 'sibling']:
            self.sibling_relationships[rel['Source']] = rel['Target']
            self.sibling_relationships[rel['Target']] = rel['Source']

    def is_spouse(self, spouse1_id: str, spouse2_id: str):
        """Check if two individuals are spouses."""
        return self.relationships[spouse1_id] == spouse2_id

    def is_parent(self, child_id: str, parent_id: str):
        """Check if param2 (parent) is a parent of param1 (child)."""
        return parent_id in self.child_to_parents.get(child_id, set())

    # Read-only methods for querying relationships
    def parent_of_child(self, parent_id, child_id):
        """Check if an individual is a parent of another."""
        return child_id in self.individuals[parent_id].children

    def are_siblings(self, individual1_id, individual2_id):
        """Check if two individuals share at least one parent."""
        parents1 = self.individuals[individual1_id].parents
        parents2 = self.individuals[individual2_id].parents
        return bool(set(parents1) & set(parents2))

    def get_family(self, family_id):
        """Retrieve a family by ID."""
        return self.families.get(family_id)

    def get_family_of_individual(self, individual_id):
        """Retrieve the family of an individual."""
        if individual_id not in self.individuals:
            raise ValueError(f"Individual ID {individual_id} not found.")
        for family in self.families.values():
            if individual_id in family.children:
                return family
            if individual_id in family.parents:
                return family
        raise ValueError(f"Unable to find family for individual ID {individual_id}.")

    def get_ancestors(self, individual_id, depth=1) -> set:
        """Retrieve ancestors up to a given depth."""
        ancestors = set()
        if not self.individual_exists(individual_id):
            return ancestors
        current_generation = {individual_id}
        for _ in range(depth):
            next_generation = set()
            for person_id in current_generation:
                next_generation.update(self.get_parents(person_id))
            ancestors.update(next_generation)
            current_generation = next_generation
        return ancestors

    def get_parents(self, child_id) -> []:
        """Retrieve the parents of an individual."""
        parents = []
        if not self.individual_exists(child_id):
            return []
        if child_id in self.child_to_parents:
            parents = self.child_to_parents[child_id]
        return parents

    def get_children(self, individual_id) -> []:
        """Retrieve the children of an individual."""
        children = []
        if not self.individual_exists(individual_id):
            return []
        if individual_id in self.parent_to_children:
            children = self.parent_to_children[individual_id]
        return children

    def get_descendents(self, individual_id, depth=1):
        """Retrieve descendents up to a given depth."""
        descendents = set()
        current_generation = {individual_id}
        for _ in range(depth):
            next_generation = set()
            for person_id in current_generation:
                next_generation.update(self.get_children(person_id))
            descendents.update(next_generation)
            current_generation = next_generation
        return descendents

    def describe_relationship(self, person1_id, person2_id):
        """Describe the relationship of person1 to person2."""
        if self.parent_of_child(person1_id, person2_id):
            return "parent"
        if self.parent_of_child(person2_id, person1_id):
            return "child"
        if self.are_siblings(person1_id, person2_id):
            return "sibling"
        if person1_id in self.get_ancestors(person2_id, depth=2) and person1_id not in self.get_ancestors(person2_id, depth=1):
            return "grandparent"
        if person1_id in self.get_descendents(person2_id, depth=2) and person1_id not in self.get_descendents(person2_id, depth=1):
            return "grandchild"
        if self.individuals[person1_id].spouse == person2_id:
            return "spouse"
        return "unknown relationship"


    def calculate_generation(self, ind_id):
        """Logic to determine generation based on parent-child relationships"""
        pass

    def is_connected(self, ind_id):
        return any(rel["Source"] == ind_id or rel["Target"] == ind_id for rel in self.relationships)

    def is_oldest_ancestor(self, ind_id):
        return len(self.get_ancestors(ind_id)) == 0


    def build_relationship_graph(self, relationship_type) -> dict:
        """
        Build a graph representation for the given relationship type.
        """
        graph = defaultdict(list)
        for rel in self.relationships:
            if rel['relationship'] == relationship_type:
                graph[rel['Source']].append(rel['Target'])
                graph[rel['Target']].append(rel['Source'])  # Assuming undirected relationships
        return graph

    @staticmethod
    def dfs_longest_chain(graph, node, visited):
        """
        Perform DFS to find the longest chain starting from the given node.
        """
        visited.add(node)
        max_chain = [node]
        for neighbor in graph[node]:
            if neighbor not in visited:
                chain = RelationshipManager.dfs_longest_chain(graph, neighbor, visited)
                if len(chain) > len(max_chain):
                    max_chain = chain
        visited.remove(node)
        return [node] + max_chain[1:]  # Include current node in the chain

    def longest_relationship_chain(self, relationship_type):
        """
        Find the longest chain of IDs for the specified relationship type.
        """
        # Build the graph
        graph = self.build_relationship_graph(self.relationships, relationship_type)

        # Find the longest chain by exploring all nodes
        longest_chain = []
        visited = set()
        for node in graph:
            chain = self.dfs_longest_chain(graph, node, visited)
            if len(chain) > len(longest_chain):
                longest_chain = chain

        return longest_chain

    def find_common_ancestor(self, individual1, individual2):
        """
        Find the most recent common ancestor between two individuals.
        :param individual1: ID of the first individual.
        :param individual2: ID of the second individual.
        :return: The most recent common ancestor or None if no common ancestor exists.
        """
        # Helper function to trace ancestors of a given individual
        def trace_ancestors(individual):
            ancestors = set()
            stack = [individual]
            while stack:
                current = stack.pop()
                if current in ancestors:
                    continue
                ancestors.add(current)
                parents = self.families.get(current, {}).get('parents', [])
                stack.extend(parents)
            return ancestors

        # Get ancestors for both individuals
        ancestors1 = trace_ancestors(individual1)
        ancestors2 = trace_ancestors(individual2)

        # Find common ancestors
        common_ancestors = ancestors1.intersection(ancestors2)

        if not common_ancestors:
            return None

        # Determine the most recent common ancestor
        def generational_distance(ancestor):
            return max(
                self.calculate_generational_distance(individual1, ancestor),
                self.calculate_generational_distance(individual2, ancestor)
            )

        most_recent_common_ancestor = min(common_ancestors, key=generational_distance)
        return most_recent_common_ancestor

    def calculate_generational_distance(self, individual1, individual2):
        """
        Calculate the generational distance between two individuals, considering relationships such as parent-child,
        siblings, and spouses.
        """
        from collections import deque

        # Ensure both individuals exist in the data
        if individual1 not in self.relationships or individual2 not in self.relationships:
            return float('inf')  # No path if one or both individuals are missing

        # BFS Initialization
        queue = deque([(individual1, 0)])  # (current individual, current distance)
        visited = set()

        while queue:
            current_individual, current_distance = queue.popleft()

            if current_individual in visited:
                continue

            visited.add(current_individual)

            # Check if we have reached the target individual
            if current_individual == individual2:
                return current_distance

            # Explore all relationships for the current individual
            for relation in self.relationships.get(current_individual, []):
                if relation not in visited:
                    queue.append((relation, current_distance + 1))

            # Include spouses in traversal (if defined separately)
            if hasattr(self, 'spouse_relationships') and current_individual in self.spouse_relationships:
                spouse = self.spouse_relationships[current_individual]
                if spouse not in visited:
                    queue.append((spouse, current_distance))  # Spouses are same generation

            # Include siblings in traversal (if defined separately)
            if hasattr(self, 'sibling_relationships') and current_individual in self.sibling_relationships:
                siblings = self.sibling_relationships[current_individual]
                for sibling in siblings:
                    if sibling not in visited:
                        queue.append((sibling, current_distance))  # Siblings are same generation

        return float('inf')  # If no path is found

    def display(self, content) -> str:
        """Pretty Print content depending on the type"""
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
            result = f"Family: {fam.id}\n{self.display(fam.husband_id)} + {self.display(fam.wife_id)} M:{fam.marr_date}\n{self.display(fam.children)}\n"

        return result


