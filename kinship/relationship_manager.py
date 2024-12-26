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
            person_a, person_b, relation_type = relation
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

    def get_relationship(self, from_id: str, to_id: str) -> str:
        """
        Determine the relationship between two individuals.
        Returns the relationship from the perspective of `from_id`.
        """
        for neighbor, relationship in self.relationship_graph[from_id]:
            if neighbor == to_id:
                return relationship
        return "No relationship found."

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
