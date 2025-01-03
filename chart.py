import yaml
import matplotlib.pyplot as plt
import networkx as nx
from kinship.family_tree_data import FamilyTreeData

# Load YAML Configuration
def load_config(path="config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# Layout Nodes Based on Configuration and Generational Rules
def layout_graph(graph, family_tree, config):
    generations = family_tree.calculate_generations()

    # Retrieve spacing weights
    weights = config.get("spacing_weights", {})
    default_spacing = config["visual"]["spacing"]["horizontal"]

    pos = {}
    y_spacing = config["visual"]["spacing"]["vertical"]
    generation_nodes = {}

    # Group nodes by generation
    for node, generation in generations.items():
        generation_nodes.setdefault(generation, []).append(node)

    # Assign positions for nodes
    for gen, nodes in sorted(generation_nodes.items()):
        for i, node in enumerate(nodes):
            # Adjust horizontal spacing based on relationship type
            spacing = default_spacing
            if i > 0:  # Compare with the previous node
                prev_node = nodes[i - 1]
                if graph.has_edge(prev_node, node):
                    relationship = graph[prev_node][node].get("relationship")
                    spacing += weights.get(relationship, 0)
            pos[node] = (i * spacing, -gen * y_spacing)

    return pos


def render_graph(graph, pos, config):
    plt.figure(figsize=(
        config["output"]["size"]["width"],
        config["output"]["size"]["height"]
    ))

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
    node_colors = [graph.nodes[node]['color'] for node in graph.nodes()]
    labels = {node: graph.nodes[node]['label'] for node in graph.nodes()}
    nx.draw(
        graph, pos,
        labels=labels,
        node_color="white", edgecolors=node_colors,
        node_size=3000, font_size=config["visual"]["labels"]["font_size"]
    )

    plt.title(config["visual"]["title"])
    plt.savefig(config["output"]["path"])
    plt.close()


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
