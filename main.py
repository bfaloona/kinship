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
            data.load_individuals_from_csv(os.path.join(sys.argv[2], "individuals.csv"))
            data.load_families_from_csv(os.path.join(sys.argv[2], "families.csv"))
            data.load_relationships_from_csv(os.path.join(sys.argv[2], "relationships.csv"))
            # TODO Add simplest validation here
            print("Data loaded from processed files successfully!")

            from statistics import mean, median
            from collections import Counter

            try:
                # Extract individuals, families, and relationships
                # Calculate basic size stats
                num_individuals = len(data.individuals)
                num_families = len(data.families)
                num_relationships = len(data.relationships)

                # Calculate stats on generations (if available)
                generations = [ind.get('generation') for ind in data.individuals if 'generation' in ind]
                if generations:
                    avg_generation = mean(generations)
                    median_generation = median(generations)
                else:
                    avg_generation = median_generation = None

                # Analyze number of relationships per individual
                source_counts = Counter(rel['Source'] for rel in data.relationships)
                target_counts = Counter(rel['Target'] for rel in data.relationships)
                relationship_counts = source_counts + target_counts
                most_connected = relationship_counts.most_common(1)
                if most_connected:
                    most_connected_id, most_connections = most_connected[0]
                else:
                    most_connected_id = most_connections = None

                # Identify any outliers in family size
                family_sizes = [len(family['members']) for family in data.families if 'members' in family]
                avg_family_size = mean(family_sizes) if family_sizes else None
                outliers = [size for size in family_sizes if
                            size > (avg_family_size * 1.5)] if avg_family_size else []

                # Print results
                print(f"Number of individuals: {num_individuals}")
                print(f"Number of families: {num_families}")
                print(f"Number of relationships: {num_relationships}")
                if avg_generation:
                    print(f"Average generation: {avg_generation}")
                    print(f"Median generation: {median_generation}")
                if most_connected_id:
                    print(f"Most connected individual: {most_connected_id} with {most_connections} connections")
                if outliers:
                    print(f"Outliers in family size: {outliers}")

                # Additional analysis (optional)
                # Example: Count unique surnames
                surnames = [ind.full_name.split()[-1] for ind in data.individuals.values()]
                unique_surnames = len(set(surnames))
                print(f"Unique surnames: {unique_surnames}:")
                for surname in set(surnames):
                    print(f"  {surname}")

            except Exception as e:
                print(f"Error analyzing family tree data: {e}")
                raise e

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"Please check the path and try again. Error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}\n{e.with_traceback(None)}")