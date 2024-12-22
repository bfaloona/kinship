import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def draw_family_tree(parser):
    # Get data from parser
    network_graph = parser.get_network_graph()
    individuals = parser.get_individuals()
    families = parser.get_families()

    # Create the graph
    G = nx.DiGraph()

    # Add individuals as nodes
    for ind_id, ind_data in individuals.items():
        G.add_node(ind_id, label=ind_data.full_name)

    # Add relationships from network graph
    for relationship in network_graph:
        G.add_edge(relationship['Source'], relationship['Target'], relationship=relationship['Relationship'])

    # Hierarchical layout for nodes
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    adjusted_pos = pos.copy()

    # Adjust spouse nodes dynamically to make room
    spouse_edges = [(family.husband_id, family.wife_id) for family in families.values() if family.husband_id and family.wife_id]
    for husband, wife in spouse_edges:
        if husband in adjusted_pos and wife in adjusted_pos:
            if adjusted_pos[husband][1] == adjusted_pos[wife][1]:  # Same y-coordinate
                adjusted_pos[wife] = (adjusted_pos[wife][0], adjusted_pos[wife][1] - 25)  # Move spouse node down

    # Draw the family tree
    plt.figure(figsize=(18, 12))
    ax = plt.gca()

    # Draw relationships
    for u, v, data in G.edges(data=True):
        x_coords = [adjusted_pos[u][0], adjusted_pos[v][0]]
        y_coords = [adjusted_pos[u][1], adjusted_pos[v][1]]
        if data["relationship"] == "parent-child":
            plt.plot(x_coords, y_coords, color="blue", linestyle="solid", linewidth=1.2)  # Parent (solid blue)
        elif data["relationship"] == "step-parent":
            plt.plot(x_coords, y_coords, color="red", linestyle="dashed", linewidth=1.5)  # Step-parent (dashed red)
        elif data["relationship"] == "sibling":
            plt.plot(x_coords, y_coords, color="lightgray", linestyle="dashed", linewidth=1)  # Sibling (dashed light gray)
        elif data["relationship"] == "spouse":
            plt.plot(x_coords, y_coords, color="black", linewidth=1.5)  # Spouse (solid black)

    # Draw the main graph
    nx.draw(
        G, adjusted_pos, with_labels=False, node_size=3000, node_color='lightblue'
    )

    # Add labels for nodes with adjusted positions
    for node, (x, y) in adjusted_pos.items():
        if G.nodes[node] and G.nodes[node]['label']:
            label = f"{G.nodes[node]['label'].split()[0]} {G.nodes[node]['label'].split()[-1][0]}. ({node})" or f"Unknown ({node})"
        else:
            label = f"Unknown ({node})"
        plt.text(
            x, y, label, fontsize=8, horizontalalignment='center', verticalalignment='center', rotation=30
        )

    plt.title("Family Tree Visualization")
    plt.show()