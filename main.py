import sys
import os
from kinship.parser import Parser

if __name__ == "__main__":
    if len(sys.argv) < 2:
        if "__loader__" in globals() and __loader__.path.endswith("pydevd.py"):
            gedcom_file_path = os.path.join("data", "shakespeare.ged")
        else:
            print("Usage: python main.py <path_to_gedcom_file>")
            print("Example: python main.py data/shakespeare.ged")
            sys.exit(1)
    else:
        gedcom_file_path = os.path.join(sys.argv[1])

    try:
        parser = Parser(gedcom_file_path)
        parser.parse()
        parser.write_individuals()
        parser.write_families()
        parser.write_lineage_map()
        parser.write_network_graph()
        print("Parsing and CSV generation completed successfully!")
    except FileNotFoundError:
        print(f"Error: File '{gedcom_file_path}' not found. Please check the path and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")