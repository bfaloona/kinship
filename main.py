from kinship.family_tree_data import FamilyTreeData
from kinship.relationship_manager import RelationshipManager
from kinship.chart import visualize_family_tree

def load_and_visualize():
    """Load CSV files and visualize the family tree."""
    # Load CSV data into FamilyTreeData
    tree_data = FamilyTreeData()
    tree_data.load_from_processed_files("data/shakes/individuals.csv", "data/shakes/families.csv")

    # Optionally process relationships using RelationshipManager
    manager = RelationshipManager(tree_data)

    # Visualize the family tree
    visualize_family_tree(manager)


def main():
    # Load and visualize the family tree
    load_and_visualize()


if __name__ == "__main__":
    main()
