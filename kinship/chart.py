import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def draw_family_tree(parser):
    # Load the data
    individuals = pd.read_csv(individuals_file)
    families = pd.read_csv(families_file)
    lineage_map = pd.read_csv(lineage_map_file)

    # Create the graph
    G = nx.DiGraph()

    # Add individuals as nodes
    for _, row in individuals.iterrows():
        G.add_node(row['Individual_ID'], label=row['Individual_Name'])

    # Add parent-child relationships
    for _, row in lineage_map.iterrows():
        if pd.notna(row['Father_ID']):
            G.add_edge(row['Father_ID'], row['Individual_ID'], relationship='parent')
        if pd.notna(row['Mother_ID']):
            G.add_edge(row['Mother_ID'], row['Individual_ID'], relationship='parent')

    # Add sibling relationships
    sibling_edges = []
    for _, row in lineage_map.iterrows():
        siblings = lineage_map[lineage_map['Father_ID'] == row['Father_ID']]['Individual_ID'].tolist()
        siblings += lineage_map[lineage_map['Mother_ID'] == row['Mother_ID']]['Individual_ID'].tolist()
        siblings = list(set(siblings) - {row['Individual_ID']})
        for sibling in siblings:
            sibling_edges.append((row['Individual_ID'], sibling))

    # Add spouse relationships
    spouse_edges = [(row['Husband_ID'], row['Wife_ID']) for _, row in families.iterrows() if pd.notna(row['Husband_ID']) and pd.notna(row['Wife_ID'])]

    # Hierarchical layout for nodes
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    adjusted_pos = pos.copy()

    # Adjust spouse nodes dynamically to make room
    for husband, wife in spouse_edges:
        if husband in adjusted_pos and wife in adjusted_pos:
            if adjusted_pos[husband][1] == adjusted_pos[wife][1]:  # Same y-coordinate
                adjusted_pos[wife] = (adjusted_pos[wife][0], adjusted_pos[wife][1] - 25)  # Move spouse node down

    # Draw the family tree
    plt.figure(figsize=(18, 12))
    ax = plt.gca()

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
            plt.plot(x_coords, y_coords, color="blue", linestyle="solid", linewidth=1.2)  # Parent (solid blue)
        elif data["relationship"] == "step-parent":
            plt.plot(x_coords, y_coords, color="red", linestyle="dashed", linewidth=1.5)  # Step-parent (dashed red)

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
