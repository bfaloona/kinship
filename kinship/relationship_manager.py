import networkx as nx

class RelationshipManager:
    def __init__(self, family_tree_data):
        if family_tree_data is None:
            raise ValueError("Family tree data cannot be None.")
        self.data = family_tree_data
        self.relationship_graph = nx.Graph()

        # Add attributes to nodes
        for individual_id, details in self.data.individuals.items():
            self.relationship_graph.add_node(
                individual_id,
                label=details['name'],
                color=self._get_node_color(details['sex'])
            )

        self._build_relationship_graph()
        # self.validate_core_relationships()

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

    def _get_node_color(self, sex):
        colors = {
            "Male": "blue",
            "Female": "red",
            "Unknown": "black"
        }
        return colors.get(sex, "black")
