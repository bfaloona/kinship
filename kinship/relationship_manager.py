import networkx as nx

class RelationshipManager:
    def __init__(self, family_tree_data):
        if family_tree_data is None:
            raise ValueError("Family tree data cannot be None.")
        self.data = family_tree_data
        self.relationship_graph = nx.Graph()
        self._build_relationship_graph()
        self.validate_core_relationships()

    def _build_relationship_graph(self):
        # Populate relationship_graph with initial data
        for family_id, family in self.data.families.items():
            if family is None:
                continue

            parents = [family['husband_id'], family['wife_id']]
            parents = [p for p in parents if p is not None]  # Filter out None values
            children = family['children'] if family['children'] else []

            # Add parent-child relationships (undirected)
            for parent in parents:
                for child in children:
                    self.relationship_graph.add_edge(parent, child, relationship='parent-child')

            # Add sibling relationships
            for i, child1 in enumerate(children):
                for child2 in children[i + 1:]:
                    self.relationship_graph.add_edge(child1, child2, relationship='sibling')

            # Add spousal relationships
            if len(parents) == 2:
                self.relationship_graph.add_edge(parents[0], parents[1], relationship='spouse')

    def _find_shared_parent(self, reference, related_to):
        reference_parents = self.data.get_parents(reference) or {}
        related_to_parents = self.data.get_parents(related_to) or {}
        return reference_parents.intersection(related_to_parents)

    def get_half_siblings(self, reference):
        half_siblings = []
        reference_parents = self.data.get_parents(reference) or {}
        if not reference_parents:
            return half_siblings

        for sibling in self.data.get_all_siblings(reference):
            shared_parents = self._find_shared_parent(reference, sibling)
            if len(shared_parents) == 1:  # Exactly one shared parent
                half_siblings.append(sibling)
        return half_siblings

    def get_step_siblings(self, reference):
        step_siblings = []
        parents = self.data.get_parents(reference) or {}
        for parent in parents:
            for spouse in self.data.get_spouses(parent):
                if not spouse:
                    continue

                spouse_children = self.data.get_children(spouse) or []
                for child in spouse_children:
                    if child != reference and child not in self.data.get_siblings(reference):
                        step_siblings.append(child)
        return step_siblings

    def get_step_parents(self, related_to):
        bio_family = self.data.get_family(related_to)
        bio_parents = self.data.get_parents(related_to) or {}
        step_parents = set()
        for family_id, family in self.data.families.items():
            if family == bio_family:
                continue
            if any(parent in bio_parents for parent in family.get_parents()):
                for parent in family.get_parents():
                    if parent not in bio_parents:
                        step_parents.add(parent)
        step_parents.discard(bio_parents)
        return step_parents

    def _bfs_to_ancestors(self, individual):
        """
        Perform BFS to find ancestors and their generation distances.
        """
        self.data.get_individual(individual)  # Check if individual exists
        ancestors = {}
        queue = [(individual, 0)]  # (current_individual, generation_distance)

        while queue:
            current, distance = queue.pop(0)
            if current in ancestors:
                continue
            ancestors[current] = distance
            for parent in self.data.get_parents(current) or []:
                queue.append((parent, distance + 1))

        return ancestors

    def _find_closest_common_ancestor(self, reference_ancestors, related_to_ancestors):
        """
        Find the closest common ancestor given two ancestor mappings.
        """
        if not reference_ancestors or not related_to_ancestors:
            return None, None, None
        common_ancestors = set(reference_ancestors.keys()) & set(related_to_ancestors.keys())
        if not common_ancestors:
            return None, None, None

        closest_common_ancestor = min(
            common_ancestors, key=lambda x: reference_ancestors[x] + related_to_ancestors[x]
        )
        reference_distance = reference_ancestors[closest_common_ancestor]
        related_to_distance = related_to_ancestors[closest_common_ancestor]

        return closest_common_ancestor, reference_distance, related_to_distance

    def calculate_cousinship(self, reference, related_to):
        if reference is None or related_to is None:
            return 'Invalid reference or related_to.'

        # Get ancestors with generation distance
        reference_ancestors = self._bfs_to_ancestors(reference)
        related_to_ancestors = self._bfs_to_ancestors(related_to)

        # Find closest common ancestor
        closest_common_ancestor, reference_distance, related_to_distance = self._find_closest_common_ancestor(
            reference_ancestors, related_to_ancestors
        )

        if not closest_common_ancestor:
            return 'No relation'

        degree = min(reference_distance, related_to_distance)
        removed = abs(reference_distance - related_to_distance)

        if removed == 0:
            return f'{degree}th cousin'
        return f'{degree}th cousin {removed} times removed'

    def get_relationship(self, reference, related_to):
        if reference is None or related_to is None:
            raise ValueError('Missing reference or related_to ID.')
        if reference == related_to:
            raise ValueError('Reference and related_to IDs are the same.')
        if not self.data.get_individual(reference) or not self.data.get_individual(related_to):
            raise ValueError('Reference or related_to ID not found in data.')

        edge_relationship = None
        if self.relationship_graph.has_edge(reference, related_to):
            edge_relationship = self.relationship_graph[reference][related_to]['relationship']
            if edge_relationship == 'spouse':
                return 'spouse'
            if edge_relationship == 'parent-child':
                if reference in self.data.get_parents(related_to):
                    return 'parent'
                elif reference in self.data.get_children(related_to):
                    return 'child'
                else:
                    raise ValueError(f"Unsupported state: {edge_relationship} between {reference} and {related_to}")

        if related_to in self.get_step_parents(related_to):
            return 'step-parent'
        if related_to in self.get_half_siblings(reference):
            return 'half-sibling'
        elif related_to in self.get_step_siblings(reference):
            return 'step-sibling'
        elif edge_relationship == 'sibling':
            return 'sibling'

        # Cousinship
        return self.calculate_cousinship(reference, related_to)

    def display_relationship(self, reference, related_to):
        relationship = self.get_relationship(reference, related_to)
        if relationship == 'parent':
            if self.data.get_husband(related_to) == reference:
                return 'father'
            elif self.data.get_wife(related_to) == reference:
                return 'mother'
        elif relationship == 'child':
            if self.data.get_individual(reference).sex == 'M':
                return 'son'
            elif self.data.get_individual(reference).sex == 'F':
                return 'daughter'
            else:
                return 'child'
        elif relationship == 'spouse':
            if self.data.get_husband(reference) == related_to:
                return 'husband'
            elif self.data.get_wife(reference) == related_to:
                return 'wife'
        elif relationship == 'sibling':
            if self.data.get_individual(reference).sex == 'M':
                return 'brother'
            elif self.data.get_individual(reference).sex == 'F':
                return 'sister'
            else:
                return 'sibling'
        return relationship

    def validate_core_relationships(self):
        # Validate that parent-child and sibling relationships are intact
        for family_id, family in self.data.families.items():
            if family is None:
                continue

            parents = [family['husband_id'], family['wife_id']]
            parents = [p for p in parents if p is not None]
            children = family['children'] if family['children'] else []

            # Check parent-child relationships
            for parent in parents:
                for child in children:
                    assert self.relationship_graph.has_edge(parent, child)
                    assert self.relationship_graph[parent][child]['relationship'] == 'parent-child'

            # Check sibling relationships
            for i, child1 in enumerate(children):
                for child2 in children[i + 1:]:
                    assert self.relationship_graph.has_edge(child1, child2)
                    assert self.relationship_graph[child1][child2]['relationship'] == 'sibling'
