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
            print("Parsing and CSV generation completed successfully!")

        elif command == "load":
            data = FamilyTreeData()
            data.load_individuals_from_csv(os.path.join(sys.argv[2], "individuals.csv"))
            data.load_families_from_csv(os.path.join(sys.argv[2], "families.csv"))
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

                # Calculate stats on generations (if available)
                generations = [ind.get('generation') for ind in data.individuals if 'generation' in ind]
                if generations:
                    avg_generation = mean(generations)
                    median_generation = median(generations)
                else:
                    avg_generation = median_generation = None

                # Statistics, data shape and outliers in rm.relationship_graph data
                num_relationships = sum(len(relations) for relations in rm.relationship_graph.values())
                most_connected_id = max(rm.relationship_graph, key=lambda x: len(rm.relationship_graph[x]))
                most_connections = len(rm.relationship_graph[most_connected_id])
                step_connections = sum(len(relations['step-sibling']) +
                                       len(relations['step-parent']) +
                                       len(relations['step-child'])
                                       for relations in rm.relationship_graph.values())
                half_connections = sum(len(relations['half-sibling']) for relations in rm.relationship_graph.values())

                print(f"Total number of step relationships: {step_connections}")
                print(f"Total number of half relationships: {half_connections}")
                print(f"Most connected individual: {most_connected_id} with {most_connections} connections")
                print(f"Total number of relationships: {num_relationships} ({num_relationships/num_individuals} relationships each for {num_individuals} individuals)")


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
                age = None
                for ind in data.individuals.values():
                    if ind.birth_date and ind.death_date:
                        age = None
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

                print(" ")
                print("Example: Print relationships between two individuals")

                name1, name2, name3, name4 = None, None, None, None
                if "William Shakespeare" in [ind.full_name for ind in data.individuals.values()]:
                    name1 = "Susanna" #
                    name2 = "Hamnet" # brother
                    name3 = "Edward" # half-brother
                    name4 = "Annette" # step-sister
                else:
                    # Collect two names from the user
                    name1 = input("Enter the first individual's name: ")
                    name2 = input("Enter the second individual's name: ")

                print(" ")

                # resolve alias to find the closest matches in all possible names
                id1, id2, id3, id4 = None, None, None, None
                for name in [name1, name2, name3, name4]:
                    if name:
                        print("Resolving alias for:", name)
                        result = session.resolve_alias(name)
                        for suggestion in result.get("suggestions", []):
                            print(f"  '{suggestion['name']}' (confidence: {suggestion['confidence']})")

                if session.alias_matched(name1):
                    id1 = session.lookup_id_by_alias(name1)
                if session.alias_matched(name2):
                    id2 = session.lookup_id_by_alias(name2)
                if name3 and session.alias_matched(name3):
                    id3 = session.lookup_id_by_alias(name3)
                if name4 and session.alias_matched(name4):
                    id4 = session.lookup_id_by_alias(name4)

                ind1 = data.get_individual(id1) if id1 else None
                ind2 = data.get_individual(id2) if id2 else None
                ind3 = data.get_individual(id3) if id3 else None
                ind4 = data.get_individual(id4) if id4 else None

                # Display individuals and their IDs
                print(f"Best match for '{name1}': {data.display(ind1)}") if ind1 else print(f"No match found for '{name1}'")
                print(f"Best match for '{name2}': {data.display(ind2)}") if ind2 else print(f"No match found for '{name2}'")
                if name3:
                    print(f"Best match for '{name3}': {data.display(ind3)}") if ind3 else print(f"No match found for '{name3}'")
                if name4:
                    print(f"Best match for '{name4}': {data.display(ind4)}") if ind4 else print(f"No match found for '{name4}'")

                if ind1 and ind2:
                    # Display the relationship between two individuals
                    relationship = rm.get_relationship(id1, id2)
                    print(f"\nRelationship between {ind1.full_name} and {ind2.full_name}: {relationship}")
                if ind1 and ind3:
                    relationship = rm.get_relationship(id1, id3)
                    print(f"\nRelationship between {ind1.full_name} and {ind3.full_name}: {relationship}")
                if ind1 and ind4:
                    relationship = rm.get_relationship(id1, id4)
                    print(f"\nRelationship between {ind1.full_name} and {ind4.full_name}: {relationship}")

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