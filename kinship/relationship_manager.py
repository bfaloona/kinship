from typing import Dict, List, Tuple, Final
from collections import defaultdict, deque

class RelationshipManager:
    def __init__(self, data):
        """
        Initialize the RelationshipManager with family tree data.
        Data should include individuals, families, and relationships.
        """
        self.individuals: Final = data.individuals
        self.families: Final = data.families
        self.relationships: Final = data.relationships
        self.data = data
        self.relationship_graph = self._build_relationship_graph()

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

    def _build_relationship_graph(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Constructs a graph where nodes are individual IDs, and edges are labeled relationships.
        Example: {"A": [("B", "parent"), ("C", "sibling")]}.
        """
        graph = defaultdict(list)

        for relation in self.relationships:
            person_a, person_b, relation_type = relation.values()
            graph[person_a].append((person_b, relation_type))
            graph[person_b].append((person_a, self._inverse_relationship(relation_type)))

        # Add half-sibling and step-sibling relationships
        for family in self.families.values():
            children = family.children
            for i in range(len(children)):
                for j in range(i + 1, len(children)):
                    child_a = children[i]
                    child_b = children[j]
                    if self.data.get_parents(child_a) != self.data.get_parents(child_b):
                        graph[child_a].append((child_b, "half-sibling"))
                        graph[child_b].append((child_a, "half-sibling"))
                    elif family.husband_id and family.wife_id:
                        graph[child_a].append((child_b, "step-sibling"))
                        graph[child_b].append((child_a, "step-sibling"))

        return graph

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
            for neighbor, relationship in self.relationship_graph[current]:
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
        print(f"_find_common_ancestor() called with a: {self.data.get_individual(person_a).full_name} b: {self.data.get_individual(person_b).full_name}")
        visited_a = self._bfs_ancestors(person_a)
        print(f"    a: {visited_a}")
        visited_b = self._bfs_ancestors(person_b)
        print(f"    b: {visited_b}")

        common_ancestors = set(visited_a.keys()).intersection(visited_b.keys())
        print(f"    common_ancestors: {common_ancestors}")
        if not common_ancestors:
            return None, -1, -1

        closest_ancestor = min(common_ancestors, key=lambda ancestor: visited_a[ancestor] + visited_b[ancestor])
        print("    closest_ancestor: ", closest_ancestor)
        return closest_ancestor, visited_a[closest_ancestor], visited_b[closest_ancestor]

    def _bfs_ancestors(self, individual_id):
        """
        Perform a breadth-first search (BFS) to find all ancestors of a given individual.

        Args:
            individual_id (str): The ID of the individual whose ancestors are to be found.

        Returns:
            dict: A dictionary where keys are ancestor IDs and values are their respective
                  distances from the given individual.
        """
        from collections import deque, defaultdict

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

    def old_method_stub(self, *args, **kwargs):
        """
        Placeholder for deprecated methods to maintain compatibility.
        """
        raise NotImplementedError("This method has been deprecated. Please use the new API.")
