from typing import List, Tuple, Dict, Set
from collections import defaultdict, deque
from .family_tree_data import FamilyTreeData

class RelationshipManager:
    def __init__(self, data: FamilyTreeData):
        self.data = data
        self.individuals = data.individuals  # Dictionary of individuals keyed by their ID
        self.families = data.families  # Dictionary of families keyed by their ID
        self.relationship_graph: Dict[str, Dict[str, Set[str]]] = {}
        self._build_relationship_graph()

    def _build_relationship_graph(self) -> None:
        """
        Build the relationship graph dynamically by integrating logic from the deprecated
        GedcomParser.build_relationships() method.
        """
        for individual_id in self.individuals:
            self.relationship_graph[individual_id] = {
                "spouse": set(),
                "parent": set(),
                "child": set(),
                "sibling": set(),
                "half-sibling": set(),
                "step-sibling": set(),
                "step-parent": set(),
                "step-child": set()
            }


        # Iterate through all families to establish parent-child and spousal relationships
        for family_id, family in self.families.items():
            spouses = [family.husband_id] if family.husband_id else []
            if family.wife_id:
                spouses.append(family.wife_id)
            children = [child_id for child_id in family.children]

            # Create spousal relationships
            if len(spouses) == 2:
                self._add_relationship(spouses[0], spouses[1], "spouse")
                self._add_relationship(spouses[1], spouses[0], "spouse")

            # Create parent-child relationships
            for parent_id in spouses:
                for child_id in children:
                    self._add_relationship(parent_id, child_id, "parent")
                    self._add_relationship(child_id, parent_id, "child")

        # Iterate through individuals to identify sibling and half-sibling relationships
        for family_id, family in self.families.items():
            for i, child1_id in enumerate(family.children):
                for child2_id in family.children[i + 1:]:
                    self._add_relationship(child1_id, child2_id, "sibling")
                    self._add_relationship(child2_id, child1_id, "sibling")

        # Add support for half-sibling relationships
        self._add_half_sibling_relationships()

    def _add_relationship(self, individual1: str, individual2: str, relationship_type: str) -> None:
        """
        Helper method to add a relationship to the graph.
        """
        self.relationship_graph[individual1][relationship_type].add(individual2)

    def _add_half_sibling_relationships(self):
        """
        Identify and add half-sibling relationships based on shared parents.
        """
        for family in self.families.values():
            parents = family.get_parents()

            # Iterate through each pair of parents to identify half-siblings
            for i, parent1 in enumerate(parents):
                for parent2 in parents[i + 1:]:
                    shared_children = set(self.relationship_graph[parent1]["child"]).intersection(
                        self.relationship_graph[parent2]["child"]
                    )

                    # Mark individuals as half-siblings
                    for child1 in shared_children:
                        for child2 in shared_children:
                            if child1 != child2:
                                self._add_relationship(child1, child2, "half-sibling")

    def _inverse_relationship(self, relation_type: str) -> str:
        """
        Returns the inverse of a relationship type.
        Example: 'parent' -> 'child', 'spouse' -> 'spouse'.
        """
        inverses = {
            "parent": "child",
            "child": "parent",
            "grandparent": "grandchild",
            "grandchild": "grandparent",
            "step-parent": "step-child",
            "step-child": "step-parent",
            "spouse": "spouse",
            "sibling": "sibling",
            "half-sibling": "half-sibling",
            "step-sibling": "step-sibling",
        }
        return inverses.get(relation_type, "unknown")

    def get_relationship(self, subject_id: str, target_id: str) -> str:
        """
        Determine the relationship between two individuals.
        Returns the relationship from the perspective of `subject_id`.
        """
        path = self._find_shortest_path(subject_id, target_id)
        if not path:
            return "No relationship found."
        derived_from_path = self._derive_relationship_from_path(path, target_id)
        if derived_from_path == "indirect relationship":
            derived__from_cousinship = self.get_cousin_relationship(subject_id, target_id)
            if derived__from_cousinship == "No cousin relationship found.":
                return derived_from_path
            else:
                return derived__from_cousinship
        else:
            return derived_from_path

    def _find_shortest_path(self, start: str, end: str) -> List[Tuple[str, str]]:
        """
        Perform BFS to find the shortest relationship path between two individuals.
        Returns the path as a list of tuples (person_id, relationship).
        """
        queue = deque([(start, [])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            if current in visited:
                continue
            visited.add(current)
            for relationship, neighbors in self.relationship_graph[current].items():
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, path + [(current, relationship)]))

        return []

    def _derive_relationship_from_path(self, path: List[Tuple[str, str]], target_id: str) -> str:
        """
        Derive the relationship type from the shortest path.
        Adds sex-based specificity (e.g., 'father'/'mother') when possible.
        """
        if len(path) == 1:
            base_relationship = path[0][1]
            return self._specific_relationship(base_relationship, target_id)

        relationships = [step[1] for step in path]

        # Handle grandparent and other indirect relationships
        if relationships == ["parent", "parent"]:
            return self._specific_relationship("grandparent", target_id)
        if relationships == ["child", "child"]:
            return self._specific_relationship("grandchild", target_id)

        # Fallback for unsupported paths
        return "indirect relationship"

    def _specific_relationship(self, relationship: str, target_id: str) -> str:
        """
        Add sex-specific context to the relationship based on the target's sex.
        """
        if relationship in {"parent", "grandparent"}:
            target_sex = self.individuals.get(target_id, {}).sex
            if target_sex == "M":
                return "father" if relationship == "parent" else "grandfather"
            elif target_sex == "F":
                return "mother" if relationship == "parent" else "grandmother"
        return relationship

    def get_cousin_relationship(self, person_a: str, person_b: str) -> str:
        """
        Calculate the cousinship between two individuals.
        """
        common_ancestor, distance_a, distance_b = self._find_common_ancestor(person_a, person_b)

        if common_ancestor:
            return self._determine_cousinship(distance_a, distance_b)
        return "No cousin relationship found."

    def _find_common_ancestor(self, person_a: str, person_b: str) -> Tuple[str, int, int]:
        """
        Find the most recent common ancestor and distances from it for two individuals.
        Returns a tuple of (common_ancestor_id, distance_to_a, distance_to_b).
        """
        visited_a = self._bfs_ancestors(person_a)
        visited_b = self._bfs_ancestors(person_b)

        common_ancestors = set(visited_a.keys()).intersection(visited_b.keys())
        if not common_ancestors:
            return None, -1, -1

        closest_ancestor = min(common_ancestors, key=lambda ancestor: visited_a[ancestor] + visited_b[ancestor])
        return closest_ancestor, visited_a[closest_ancestor], visited_b[closest_ancestor]

    def _bfs_ancestors(self, individual_id: str) -> Dict[str, int]:
        """
        Perform a breadth-first search (BFS) to find all ancestors of a given individual.
        Returns a dictionary where keys are ancestor IDs and values are their respective distances from the given individual.
        """
        ancestors = defaultdict(int)
        queue = deque([(individual_id, 0)])
        visited = set()

        while queue:
            current_id, distance = queue.popleft()
            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id != individual_id:
                ancestors[current_id] = distance

            parents = self.data.get_parents(current_id)
            for parent in parents:
                if parent not in visited:
                    queue.append((parent, distance + 1))

        return dict(ancestors)

    def _determine_cousinship(self, distance_a: int, distance_b: int) -> str:
        """
        Calculate the cousinship and removal based on ancestor distances.
        """
        if distance_a == distance_b:
            cousin_level = distance_a - 1
            return f"{cousin_level}th cousin"
        removal = abs(distance_a - distance_b)
        cousin_level = min(distance_a, distance_b) - 1
        return f"{cousin_level}th cousin {removal} times removed"