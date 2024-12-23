from typing import Final
from collections import defaultdict

from kinship.individual import Individual
from kinship.family import Family
from kinship.parser import create_parent_to_children, create_parent_to_step_children #noqa F401


class RelationshipManager:
    def __init__(self, individuals, families, relationships, parser=None):
        """Store data in read-only format."""
        self._individuals: Final = individuals
        self._families: Final = families
        self._relationships: Final = relationships
        self._parser: Final = parser
        self.child_to_parents = {}
        for fam in self._families.values():
            for child in fam.children:
                self.child_to_parents[child.id] = {fam.husband_id, fam.wife_id}
        self.parent_to_children = create_parent_to_children(self._families)
        self.parent_to_step_children = create_parent_to_step_children(self._families, self.parent_to_children)

    def individual_exists(self, individual_id):
        """Check if the individual ID is valid."""
        if individual_id not in self._individuals:
            print(f"Individual ID {individual_id} not found.")
            return False
        return True
    # Read-only methods for querying relationships
    def parent_of_child(self, parent_id, child_id):
        """Check if an individual is a parent of another."""
        return child_id in self._individuals[parent_id].children

    def are_siblings(self, individual1_id, individual2_id):
        """Check if two individuals share at least one parent."""
        parents1 = self._individuals[individual1_id].parents
        parents2 = self._individuals[individual2_id].parents
        return bool(set(parents1) & set(parents2))

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

    def get_parents(self, individual_id) -> []:
        """Retrieve the parents of an individual."""
        parents = []
        if not self.individual_exists(individual_id):
            return []
        if individual_id in self._child_to_parents:
            parents = self._child_to_parents[individual_id]
        return parents

    def get_children(self, individual_id) -> []:
        """Retrieve the children of an individual."""
        children = []
        if not self.individual_exists(individual_id):
            return []
        if individual_id in self._parent_to_children:
            children = self._parent_to_children[individual_id]
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

    def get_family(self, family_id) -> Family:
        """Retrieve the family details for a given family ID."""
        return self._families.get(family_id)

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
        if self._individuals[person1_id].spouse == person2_id:
            return "spouse"
        return "unknown relationship"


    def calculate_generation(self, ind_id):
        """Logic to determine generation based on parent-child relationships"""
        pass

    def is_connected(self, ind_id):
        return any(rel["Source"] == ind_id or rel["Target"] == ind_id for rel in self._relationships)

    def is_oldest_ancestor(self, ind_id):
        return len(self.get_ancestors(ind_id)) == 0


    def build_relationship_graph(self, relationship_type) -> dict:
        """
        Build a graph representation for the given relationship type.
        """
        graph = defaultdict(list)
        for rel in self._relationships:
            if rel['relationship'] == relationship_type:
                graph[rel['source_id']].append(rel['target_id'])
                graph[rel['target_id']].append(rel['source_id'])  # Assuming undirected relationships
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
        graph = self.build_relationship_graph(self._relationships, relationship_type)

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
                parents = self._families.get(current, {}).get('parents', [])
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

    def calculate_generational_distance(self, individual, ancestor):
        """
        Calculate the number of generations between an individual and an ancestor.
        :param individual: ID of the individual.
        :param ancestor: ID of the ancestor.
        :return: Number of generations or a large number if no relationship exists.
        """
        queue = [(individual, 0)]  # (current_individual, generation_count)
        visited = set()

        while queue:
            current, generations = queue.pop(0)

            if current == ancestor:
                return generations

            if current in visited:
                continue

            visited.add(current)
            parents = self._families.get(current, {}).get('parents', [])
            queue.extend((parent, generations + 1) for parent in parents)

        return float('inf')  # If no path exists to the ancestor


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
            if content in self._individuals:
                result = self.display(self._individuals[content])
            else:
                result = content

        elif isinstance(content, Individual):
            result = f"{content.full_name} ({content.id})"

        elif isinstance(content, Family):
            fam = content
            result = f"Family: {fam.id}\n{self.display(fam.husband_id)} + {self.display(fam.wife_id)} M:{fam.marr_date}\n{self.display(fam.children)}\n"

        return result