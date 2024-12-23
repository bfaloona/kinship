import sys
import os

from kinship.family_tree_data import FamilyTreeData
from kinship.gedcom_parser import GedcomParser
from kinship.relationship_manager import RelationshipManager

if __name__ == "__main__":
    if len(sys.argv) < 2:
        if "__loader__" in globals() and __loader__.path.endswith("pydevd.py"):
            gedcom_file_path = os.path.join("data", "FamilyTree.ged")
        else:
            print("Usage: python main.py <path_to_gedcom_file>")
            print("Example: python main.py data/shakespeare.ged")
            sys.exit(1)
    else:
        gedcom_file_path = os.path.join(sys.argv[1])

    try:
        parser = GedcomParser(gedcom_file_path)
        parser.parse_gedcom_file()
        data = FamilyTreeData()
        data.load_from_gedcom(parser)
        parser.write_individuals()
        parser.write_families()
        parser.write_relationships()
        print("Parsing and CSV generation completed successfully!")

        rm = RelationshipManager(parser.individuals,
                                 parser.families,
                                 parser.relationships,
                                 parser)
        id = "I0001"
        fam_id = "F12"
        print(f"### Ancestors of {rm.display(id)}:")
        print(rm.display(rm.get_ancestors(id, depth=4)))
        print(f"### Descendents of {rm.display(id)}:")
        print(rm.display(rm.get_descendents(id, depth=4)))
        print(f"### Parents of {rm.display(id)}:")
        print(rm.display(rm.get_parents(id)))
        print(f"### Family ({rm.display(fam_id)}) of {rm.display(id)}:")
        print(rm.display(rm.get_family(fam_id)))
        # print(f"### Spouses of ({rm.display(fam_id)}) of {rm.display(id)}:")
        # print(rm.display(rm.get_spouses(fam_id)))
        # print(f"### Children of ({rm.display(fam_id)}) of {rm.display(id)}:")
        # print(rm.display(rm.get_childen(fam_id)))
        # print(f"### Step Children of ({rm.display(fam_id)}) of {rm.display(id)}:")
        # print(rm.display(rm.get_step_children(fam_id)))

        # chart.draw_family_tree(rm)
        # print("Family tree chart generated successfully!")

    except FileNotFoundError as e:
        print(f"Please check the path and try again. Error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}\n{e.with_traceback(None)}")