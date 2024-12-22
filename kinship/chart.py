import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def draw_family_tree(parser):
    # Get data from parser
    network_graph = parser.get_network_graph()
    individuals = parser.get_individuals()
    # families = parser.get_families()

    # Create the graph
    G = nx.DiGraph()

    # Add individuals as nodes
    for ind_id, ind_data in individuals.items():
        G.add_node(ind_id, label=f"{ind_data.full_name}\n{ind_id}")

    sibling_edges = []
    spouse_edges = []
    # Add relationships from network graph
    for relationship in network_graph:
        G.add_edge(relationship['Source'], relationship['Target'], relationship=relationship['Relationship'])
        if relationship['Relationship'] == 'sibling':
            sibling_edges.append([relationship['Source'], relationship['Target']])
        if relationship['Relationship'] == 'spouse':
            spouse_edges.append([relationship['Source'], relationship['Target']])

    # Hierarchical layout for nodes
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    adjusted_pos = pos.copy()

    # Draw sibling relationships (light gray dashed lines)
    for u, v in sibling_edges:
        if u in adjusted_pos and v in adjusted_pos:
            x_coords = [adjusted_pos[u][0], adjusted_pos[v][0]]
            y_coords = [adjusted_pos[u][1], adjusted_pos[v][1]]
            plt.plot(x_coords, y_coords, color="lightgray", linestyle="dashed", linewidth=1)

    # Draw spouse relationships (black solid lines)
    for husband, wife in spouse_edges:
        if husband in adjusted_pos and wife in adjusted_pos:
            x_coords = [adjusted_pos[husband][0], adjusted_pos[wife][0]]
            y_coords = [adjusted_pos[husband][1], adjusted_pos[wife][1]]
            plt.plot(x_coords, y_coords, color="black", linewidth=1.5)

    # Draw parent and step-parent edges
    for u, v, data in G.edges(data=True):
        x_coords = [adjusted_pos[u][0], adjusted_pos[v][0]]
        y_coords = [adjusted_pos[u][1], adjusted_pos[v][1]]
        if data["relationship"] == "parent":
            plt.plot(x_coords, y_coords, color="blue", linestyle="solid", linewidth=1.5)  # Parent
        elif data["relationship"] == "step-parent":
            plt.plot(x_coords, y_coords, color="blue", linestyle="dashed", linewidth=1.2)  # Step-parent

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
