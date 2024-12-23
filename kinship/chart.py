import pygraphviz as pgv
from .relationship_manager import RelationshipManager

def draw_family_tree(rm: RelationshipManager):
    # Get data from parser
    relationships = rm.relationships
    individuals = rm.individuals

    # Determine generations based on relationships
    generations = {}  # Maps individual ID to generation level
    for ind_id in individuals.keys():
        generations[ind_id] = rm.calculate_generation(ind_id)

    # Create the PyGraphviz graph
    G = pgv.AGraph(directed=True)
    G.graph_attr.update(
        size="20,15!",
        splines="polyline",
        overlap="prism",
        rankdir="TB",
        dpi="150"
    )

    sibling_edges = []
    spouse_edges = []

    # Add individuals as nodes
    for ind_id, ind_data in individuals.items():
        generation = generations[ind_id]
        G.add_node(
            ind_id,
            label=f"{ind_data.full_name}\n({ind_id})",
            shape="ellipse",
            style="filled",
            fillcolor="lightblue",
            fontname="Arial Bold",
            fontsize="14",
            margin="0.3,0.3"
        )
        # Assign ranks based on generation
        G.node_attr[ind_id]["rank"] = f"{generation}"

    # Add relationships and group siblings, spouses
    for relationship in relationships:
        G.add_edge(
            relationship["Source"],
            relationship["Target"],
            label=relationship["Relationship"],
            fontsize="10"
        )
        if relationship["Relationship"] == "sibling":
            sibling_edges.append([relationship["Source"], relationship["Target"]])
        elif relationship["Relationship"] == "spouse":
            spouse_edges.append([relationship["Source"], relationship["Target"]])

    # Group siblings horizontally within a generation
    for sibling1, sibling2 in sibling_edges:
        G.add_edge(sibling1, sibling2, style="dotted", color="gray", constraint="false")

    # Place spouses near each other
    for husband, wife in spouse_edges:
        G.add_edge(husband, wife, style="dashed", color="black", constraint="false")

    # Isolate unrelated individuals
    for ind_id in individuals.keys():
        if not rm.is_connected(ind_id):
            G.add_node(ind_id, group="isolated")

    # Use hierarchical layout
    G.layout(prog="dot")
    G.draw("family_tree_generations.png", format="png")

    # Display using matplotlib
    # plt.figure(figsize=(25, 20))
    # plt.imshow(plt.imread("family_tree_generations.png"))
    # plt.axis("off")
    # plt.title("Family Tree by Generations", fontsize=20, fontweight="bold")
    # plt.show()

