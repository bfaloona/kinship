import pygraphviz as pgv
import matplotlib.pyplot as plt

def draw_family_tree(parser):
    # Get data from parser
    network_graph = parser.get_network_graph()
    individuals = parser.get_individuals()

    # Create the PyGraphviz graph
    G = pgv.AGraph(directed=True)
    G.graph_attr.update(
        size="15,10!",
        splines="line",  # Straight edges for clarity
        overlap="prism",
        rankdir="TB",  # Top-to-bottom layout
        ranksep="4.0",
        nodesep="2.5",
        dpi="150",
        page="8.5,11",  # Fit within printable page dimensions
        ratio="compress"
    )

    # Add individuals as nodes
    for ind_id, ind_data in individuals.items():
        G.add_node(
            ind_id,
            label=f"{ind_data.full_name}\n({ind_id})",
            shape="ellipse",
            style="filled",
            fillcolor="lightblue",
            fontname="Arial Bold",
            fontsize="14",
            margin="0.5,0.5"
        )

    # Add relationships from network graph
    for relationship in network_graph:
        G.add_edge(
            relationship["Source"],
            relationship["Target"],
            label=relationship["Relationship"],
            fontsize="10"
        )

    # Use circular layout for better edge routing
    G.layout(prog="circo")
    G.draw("family_tree_final.png", format="png")

    # Display using matplotlib
    plt.figure(figsize=(25, 20))
    plt.imshow(plt.imread("family_tree_final.png"))
    plt.axis("off")
    plt.title("Final Family Tree Visualization", fontsize=20, fontweight="bold")
    plt.show()
