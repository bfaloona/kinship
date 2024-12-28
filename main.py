import sys
import os

from kinship.family_tree_data import FamilyTreeData
from kinship.gedcom_parser import GedcomParser
from kinship.relationship_manager import RelationshipManager
from kinship.session_context import SessionContext

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

            session = SessionContext({key: ind.full_name for key, ind in data.individuals.items()})
            rm = RelationshipManager(data)

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
                print(" ")

                # Example: Count the number of males and females
                num_males = sum(1 for ind in data.individuals.values() if ind.sex == 'M')
                num_females = sum(1 for ind in data.individuals.values() if ind.sex == 'F')
                print(f"Number of males: {num_males}")
                print(f"Number of females: {num_females}")

                # Example: Find the oldest and youngest individuals
                individuals_by_birth_date = sorted(data.individuals.values(), key=lambda ind: ind.birth_date)
                oldest_individual = individuals_by_birth_date[0]
                youngest_individual = individuals_by_birth_date[-1]
                print(f"Oldest individual: {oldest_individual.full_name} (born {oldest_individual.birth_date})")
                print(f"Youngest individual: {youngest_individual.full_name} (born {youngest_individual.birth_date})")

                # Example: Calculate the average lifespan
                lifespans = []
                for ind in data.individuals.values():
                    if ind.birth_date and ind.death_date:
                        try:
                            age = (ind.death_date - ind.birth_date).days / 365.25
                        except (AttributeError, TypeError):
                            age = None
                    lifespans.append(age) if age else None
                average_lifespan = mean(lifespans) if lifespans else None

                print(
                    f"Average lifespan: {average_lifespan:.2f} years" if average_lifespan else "Average lifespan: N/A")

                # Example: Find the most common first name
                first_names = [ind.full_name.split()[0] for ind in data.individuals.values()]
                most_common_first_name = Counter(first_names).most_common(1)
                if most_common_first_name:
                    print(
                        f"Most common first name: {most_common_first_name[0][0]} (count: {most_common_first_name[0][1]})")

                # Example: Print relationships between two individuals

                # Collect two names from the user
                # name1 = input("Enter the first name: ")
                # name2 = input("Enter the second name: ")
                name1 = "Anne H"
                name2 = "William"

                # Perform fuzzy matching to find the closest matches in all possible names
                # all_names = [ind.full_name for ind in data.individuals.values()]
                # best_match1 = process.extractOne(name1, all_names)
                # best_match2 = process.extractOne(name2, all_names)
                id1, id2 = None, None
                if session.alias_matched(name1):
                    id1 = session.lookup_id_by_alias(name1)
                if session.alias_matched(name2):
                    id2 = session.lookup_id_by_alias(name2)

                ind1 = data.get_individual(id1) if id1 else None
                ind2 = data.get_individual(id2) if id2 else None
                # Display individuals and their IDs
                print(f"Best match for '{name1}': {data.display(ind1)}") if ind1 else print(f"No match found for '{name1}'")
                print(f"Best match for '{name2}': {data.display(ind2)}") if ind2 else print(f"No match found for '{name2}'")

                if ind1 and ind2:
                    # Display the relationship between the two individuals
                    relationship = rm.get_relationship(id1, id2)
                    print(f"Relationship between {ind1.full_name} and {ind2.full_name}: {relationship}")

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