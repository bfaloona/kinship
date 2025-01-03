import yaml
import matplotlib.pyplot as plt
import networkx as nx


# Load YAML Configuration
def load_config(path="chart-config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# Layout Nodes Based on Configuration and Generational Rules
def layout_graph(graph, family_tree, config):
    generations = family_tree.calculate_generations()

    # Horizontal generational layout
    pos = {}
    y_spacing = config["visual"]["spacing"]["vertical"]
    x_spacing = config["visual"]["spacing"]["horizontal"]
    generation_nodes = {}

    # Group nodes by generation
    for node, generation in generations.items():
        generation_nodes.setdefault(generation, []).append(node)

    # Assign positions for nodes
    for gen, nodes in sorted(generation_nodes.items()):
        for i, node in enumerate(nodes):
            pos[node] = (i * x_spacing, -gen * y_spacing)

    return pos


# Render and Save Visualization
def render_graph(graph, pos, config):
    plt.figure(figsize=(
        config["output"]["size"]["width"],
        config["output"]["size"]["height"]
    ))

    # Debugging: Log missing positions
    for edge in graph.edges(data=True):
        if edge[0] not in pos or edge[1] not in pos:
            print(f"Missing position for edge: {edge}")

    # Draw edges
    for edge in graph.edges(data=True):
        if edge[0] in pos and edge[1] in pos:  # Validate node positions
            relationship = edge[2].get("relationship")
            style = config["visual"]["line_styles"].get(relationship, {})
            nx.draw_networkx_edges(
                graph, pos, edgelist=[(edge[0], edge[1])],
                edge_color=style.get("color", "black"),
                style=style.get("style", "solid"),
                width=style.get("width", 1)
            )

    # Draw nodes
    node_colors = [graph.nodes[node].get("color", "black") for node in graph.nodes()]
    labels = nx.get_node_attributes(graph, "label")
    nx.draw(
        graph, pos,
        labels=labels,
        node_color="white", edgecolors=node_colors,
        node_size=3000, font_size=config["visual"]["labels"]["font_size"]
    )

    # Save the graph
    plt.title(config["visual"]["title"])
    plt.savefig(config["output"]["path"])
    plt.close()


# Extend FamilyTreeData with calculate_generations method
class FamilyTreeData:
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

    def load_families_from_csv(self, file_path):
        import csv

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                family_id = row['Family_ID']
                if family_id not in self.families:
                    self.families[family_id] = {
                        'husband_id': row['Husband_ID'],
                        'wife_id': row['Wife_ID'],
                        'children': []
                    }
                self.families[family_id]['children'].append(row['Child_ID'])

    def load_individuals_from_csv(self, file_path):
        import csv
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.individuals[row['Individual_ID']] = {
                    'name': row['Individual_Name'],
                    'sex': row['Sex'],
                    'birth_date': row['Birth_Date'],
                    'birth_place': row['Birth_Place'],
                    'death_date': row['Death_Date'],
                    'death_place': row['Death_Place']
                }

    def calculate_generations(self):
        generations = {}

        # Initialize generations for individuals without parents
        for individual_id in self.individuals:
            generations[individual_id] = 0

        updated = True
        while updated:
            updated = False
            for family in self.families.values():
                for child_id in family['children']:
                    for parent_id in [family['husband_id'], family['wife_id']]:
                        if parent_id and parent_id in generations:
                            new_gen = generations[parent_id] + 1
                            if child_id not in generations or generations[child_id] < new_gen:
                                generations[child_id] = new_gen
                                updated = True

        return generations


# Main Execution
def main():
    # Load configuration
    config = load_config()

    # Access FamilyTreeData and RelationshipManager
    from kinship.relationship_manager import RelationshipManager

    family_tree = FamilyTreeData()
    family_tree.load_from_processed_files("data/shakes/individuals.csv", "data/shakes/families.csv")
    manager = RelationshipManager(family_tree)

    # Use the relationship_graph from RelationshipManager
    graph = manager.relationship_graph

    # Filter graph to include only valid nodes
    valid_nodes = {node for node in graph.nodes() if node}  # Ensure nodes are non-empty
    graph = graph.subgraph(valid_nodes).copy()  # Retain only valid nodes

    # Generate layout and render the graph
    pos = layout_graph(graph, family_tree, config)
    render_graph(graph, pos, config)


if __name__ == "__main__":
    main()
