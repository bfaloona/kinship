import sys
import os

from kinship.family_tree_data import FamilyTreeData
from kinship.relationship_manager import RelationshipManager
from kinship.session_context import SessionContext


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python command.py <command> <path_to_file>")
        print("Commands: parse, load")
        print("Example: python command.py parse data/shakespeare.ged")
        sys.exit(1)
    else:
        command = sys.argv[1]

    try:
        if command == "parse":
            from parser.gedcom_parser import GedcomParser

            file_path = os.path.join(sys.argv[2])
            parser = GedcomParser(file_path)
            parser.parse_gedcom_file()
            data = FamilyTreeData()
            data.individuals = parser.get_individuals()
            data.families = parser.get_families()
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
                generations = [ind.generation for ind in data.individuals.values() if hasattr(ind, 'generation')]
                if generations:
                    avg_generation = mean(generations)
                    median_generation = median(generations)
                else:
                    avg_generation = median_generation = None

                # Statistics, data shape and outliers in rm.relationship_graph data
                num_relationships = rm.relationship_graph.number_of_edges()
                most_connected_id = max(rm.relationship_graph, key=lambda x: rm.relationship_graph.degree(x))
                most_connections = rm.relationship_graph.degree(most_connected_id)
                step_connections = sum(1 for u, v, data in rm.relationship_graph.edges(data=True) if
                                       data.get('relationship') in ['step-sibling', 'step-parent', 'step-child'])
                half_connections = sum(1 for u, v, data in rm.relationship_graph.edges(data=True) if
                                       data.get('relationship') == 'half-sibling')

                print(f"Total number of step relationships: {step_connections}")
                print(f"Total number of half relationships: {half_connections}")
                print(f"Most connected individual: {most_connected_id} with {most_connections} connections")
                print(f"Total number of relationships: {num_relationships}")

                # Identify any outliers in family size
                family_sizes = [len(family.members) for family in data.families.values() if hasattr(family, 'members')]
                avg_family_size = mean(family_sizes) if family_sizes else None
                outliers = [size for size in family_sizes if size > (avg_family_size * 1.5)] if avg_family_size else []

                # Print results
                print(f"Number of individuals: {num_individuals}")
                print(f"Number of families: {num_families}")
                if avg_generation:
                    print(f"Average generation: {avg_generation}")
                    print(f"Median generation: {median_generation}")
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
                oldest_individual = individuals_by_birth_date[0] if individuals_by_birth_date else None
                youngest_individual = individuals_by_birth_date[-1] if individuals_by_birth_date else None
                if oldest_individual:
                    print(f"Oldest individual: {oldest_individual.full_name} (born {oldest_individual.birth_date})")
                else:
                    print("No individuals found to determine the oldest individual.")
                if youngest_individual:
                    print(
                        f"Youngest individual: {youngest_individual.full_name} (born {youngest_individual.birth_date})")
                else:
                    print("No individuals found to determine the youngest individual.")

                # Example: Calculate the average lifespan
                lifespans = []
                for ind in data.individuals.values():
                    if ind.birth_date and ind.death_date:
                        try:
                            age = (ind.death_date - ind.birth_date).days / 365.25
                            lifespans.append(age)
                        except (AttributeError, TypeError):
                            continue
                average_lifespan = mean(lifespans) if lifespans else None
                print(
                    f"Average lifespan: {average_lifespan:.2f} years" if average_lifespan else "Average lifespan: N/A")

                # Example: Find the most common first name
                first_names = [ind.full_name.split()[0] for ind in data.individuals.values()]
                most_common_first_name = Counter(first_names).most_common(1)
                if most_common_first_name:
                    print(
                        f"Most common first name: {most_common_first_name[0][0]} (count: {most_common_first_name[0][1]})")
                else:
                    print("No common first name found.")
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
                    relationship = rm.display_relationship(id1, id2)
                    print(f"\nRelationship between {ind1.full_name} and {ind2.full_name}: {relationship}")
                if ind1 and ind3:
                    relationship = rm.display_relationship(id1, id3)
                    print(f"\nRelationship between {ind1.full_name} and {ind3.full_name}: {relationship}")
                if ind1 and ind4:
                    relationship = rm.display_relationship(id1, id4)
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