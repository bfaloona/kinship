import networkx as nx
import matplotlib.pyplot as plt


def visualize_family_tree(manager):
    """
    Visualize the family tree using the RelationshipManager's graph.

    Args:
        manager (RelationshipManager): The relationship manager containing the graph.
    """
    G = manager.relationship_graph  # Use the existing graph

    pos = nx.spring_layout(G)  # Generate positions for nodes
    labels = nx.get_node_attributes(G, 'label')  # Node labels from graph attributes

    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=labels,
        node_size=3000,
        font_size=10,
        edge_color='gray',  # Edge styling
    )
    edge_labels = nx.get_edge_attributes(G, 'relationship')  # Edge relationship labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Family Tree Visualization")
    plt.show()
