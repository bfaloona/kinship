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
        self.relationship_graph = self._build_relationship_graph()

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

        return graph

    def _inverse_relationship(self, relation_type: str) -> str:
        """
        Returns the inverse of a relationship type.
        Example: 'parent' -> 'child', 'spouse' -> 'spouse'.
        """
        inverses = {
            "parent": "child",
            "child": "parent",
            "spouse": "spouse",
            "sibling": "sibling",
            "step-parent": "step-child",
            "step-child": "step-parent"
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
        return self._derive_relationship_from_path(path, target_id)

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
        visited_a = self._bfs_ancestors(person_a)
        visited_b = self._bfs_ancestors(person_b)

        common_ancestors = set(visited_a.keys()).intersection(visited_b.keys())
        if not common_ancestors:
            return None, -1, -1

        closest_ancestor = min(common_ancestors, key=lambda ancestor: visited_a[ancestor] + visited_b[ancestor])
        return closest_ancestor, visited_a[closest_ancestor], visited_b[closest_ancestor]

    def _bfs_ancestors(self, person: str) -> Dict[str, int]:
        """
        Perform BFS to find all ancestors of a person and their distances.
        """
        queue = deque([(person, 0)])
        visited = {}

        while queue:
            current, depth = queue.popleft()
            if current in visited:
                continue
            visited[current] = depth
            for neighbor, relationship in self.relationship_graph[current]:
                if relationship == "parent":
                    queue.append((neighbor, depth + 1))

        return visited

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
