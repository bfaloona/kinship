import sys
import os

from kinship.family_tree_data import FamilyTreeData
from kinship.gedcom_parser import GedcomParser

if __name__ == "__main__":
    if len(sys.argv) < 2:
        if "__loader__" in globals() and __loader__.path.endswith("pydevd.py"):
            command = "parse"
            gedcom_file_path = os.path.join("data", "shakespeare.ged")
        else:
            print("Usage: python main.py <command> <path_to_file>")
            print("Commands: parse, load")
            print("Example: python main.py parse data/shakespeare.ged")
            sys.exit(1)
    else:
        command = sys.argv[1]

    try:
        if command == "parse":
            file_path = os.path.join(sys.argv[2])
            parser = GedcomParser(file_path)
            parser.parse_gedcom_file()
            data = FamilyTreeData()
            data.load_from_gedcom(parser)
            parser.write_individuals()
            parser.write_families()
            parser.write_relationships()
            print("Parsing and CSV generation completed successfully!")

        elif command == "load":
            data = FamilyTreeData()
            data.load_individuals_from_csv("data/individuals.csv")
            data.load_families_from_csv("data/families.csv")
            data.load_relationships_from_csv("data/relationships.csv")
            print("Data loaded from processed files successfully!")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"Please check the path and try again. Error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}\n{e.with_traceback(None)}")