import yaml
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from kinship.family_tree_data import FamilyTreeData

# Load YAML Configuration
def load_config(path="config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

# Helper for curved edges
def draw_curved_edge(ax, pos, node1, node2, curvature=0.2, color="gray", linewidth=2):
    start = np.array(pos[node1])
    end = np.array(pos[node2])
    mid = (start + end) / 2
    offset = curvature * np.array([-1 * (end[1] - start[1]), end[0] - start[0]])
    control = mid + offset
    bezier = np.linspace(0, 1, 100)
    curve = (1 - bezier)[:, None]**2 * start + \
            2 * (1 - bezier)[:, None] * bezier[:, None] * control + \
            bezier[:, None]**2 * end
    ax.plot(curve[:, 0], curve[:, 1], color=color, linewidth=linewidth)


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


def layout_graph2(graph, family_tree, config):
    # Initialize positions
    pos = {}
    generation_nodes = {}
    child_counts = {}  # Track number of children for each node

    # Group nodes by generation
    generations = family_tree.calculate_generations()
    for node, generation in generations.items():
        generation_nodes.setdefault(generation, []).append(node)
        child_counts[node] = len(family_tree.get_children(node))

    y_spacing = config["visual"]["spacing"]["vertical"]
    x_spacing = config["visual"]["spacing"]["horizontal"]

    # Place nodes generation by generation
    for gen, nodes in sorted(generation_nodes.items()):
        x_offset = 0
        for node in nodes:
            # Handle spouses
            spouses = family_tree.get_spouses(node)
            if spouses:
                for spouse in spouses:
                    if spouse in pos:  # Skip already positioned spouses
                        continue
                    pos[node] = (x_offset, -gen * y_spacing)
                    pos[spouse] = (x_offset + x_spacing, -gen * y_spacing)
                    x_offset += 2 * x_spacing
            elif node not in pos:  # Place individual nodes
                pos[node] = (x_offset, -gen * y_spacing)
                x_offset += x_spacing

        # Adjust spacing based on child counts
        for node in nodes:
            children = family_tree.get_children(node)
            if children:
                child_x_start = pos[node][0] - (len(children) - 1) * x_spacing / 2
                for i, child in enumerate(children):
                    pos[child] = (child_x_start + i * x_spacing, -(gen + 1) * y_spacing)

    return pos

def render_graph(graph, pos, config):
    fig, ax = plt.subplots(figsize=(
        config["output"]["size"]["width"],
        config["output"]["size"]["height"]
    ))

    # Draw edges
    for edge in graph.edges(data=True):
        if edge[0] in pos and edge[1] in pos:  # Validate node positions
            relationship = edge[2].get("relationship")
            style = config["visual"]["line_styles"].get(relationship, {})
            if relationship == "sibling":
                draw_curved_edge(ax, pos, edge[0], edge[1], curvature=0.2)
            else:
                nx.draw_networkx_edges(
                    graph, pos, edgelist=[(edge[0], edge[1])],
                    edge_color=style.get("color", "gray"),
                    style=style.get("style", "solid"),
                    width=style.get("width", 0.5)
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
    pos = layout_graph2(graph, family_tree, config)
    render_graph(graph, pos, config)


if __name__ == "__main__":
    main()
