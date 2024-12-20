import os
import csv
import datetime
from typing import Dict, List
from ged4py.parser import GedcomReader
from .individual import Individual
from .family import Family
from .child import Child
from .util import normalize_id


class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.base_gedcom_filename = os.path.splitext(os.path.basename(file_path))[0]
        self.individuals: Dict[str, Individual] = {}
        self.families: Dict[str, Family] = {}
        self.child_to_biological_parents: Dict[str, List[str]] = {}

    def parse(self):
        with GedcomReader(self.file_path) as ged_parser:
            for individual in ged_parser.records0("INDI"):
                self.parse_individual(individual)
            for family in ged_parser.records0("FAM"):
                fam = self.parse_family(family)
                for child in self.families[fam.id].children:
                    self.child_to_biological_parents[child.id] = [
                        fam.husband_id,
                        fam.wife_id,
                    ]
        self.add_step_children()

    def parse_individual(self, individual):
        try:
            name = individual.name.format()
        except AttributeError:
            name = individual.sub_tag_value("NAME") or "Unknown"
        birth_date = individual.sub_tag_value("BIRT/DATE")
        birth_place = individual.sub_tag_value("BIRT/PLAC")
        death_date = individual.sub_tag_value("DEAT/DATE")
        death_place = individual.sub_tag_value("DEAT/PLAC")
        ind = Individual(
            normalize_id(individual.xref_id), name, birth_date, birth_place, death_date, death_place
        )
        self.individuals[ind.id] = ind

    def parse_family(self, family):
        husband = family.sub_tag("HUSB")
        wife = family.sub_tag("WIFE")
        children_records = family.sub_tags("CHIL")
        marr_date = family.sub_tag_value("MARR/DATE")  # Ensure it's a single value
        children = [Child(child.xref_id, child.name) for child in children_records]
        if husband and normalize_id(husband.xref_id) not in self.individuals:
            print(
                f"Warning: Husband ID {husband.xref_id} not found in individuals list."
            )
        if wife and normalize_id(wife.xref_id) not in self.individuals:
            print(f"Warning: Wife ID {wife.xref_id} not found in individuals list.")
        fam = Family(
            family.xref_id,
            husband if husband else None,
            wife if wife else None,
            marr_date if marr_date else None,
            children,
            []
        )
        self.families[fam.id] = fam
        return fam

    def add_step_children(self):
        # Step 1: Create a global mapping of parent → children
        parent_to_children = {}
        for family in self.families.values():
            for parent_id in [family.husband_id, family.wife_id]:
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = set()
                for child in family.children:
                    parent_to_children[parent_id].add(child.id)

        # Step 2: Compare children across families to identify step-children
        for family in self.families.values():
            biological_children = set(child.id for child in family.children)
            step_children = set()

            for parent_id in [family.husband_id, family.wife_id]:
                for other_family_id, other_family in self.families.items():
                    if other_family_id != family.id:
                        # Add step-children if they are not biological children
                        for child in other_family.children:
                            if (
                                child.id not in biological_children
                                and child.id in parent_to_children.get(parent_id, set())
                            ):
                                step_children.add(child)

            # Append unique step-children to the family
            for step_child in step_children:
                if step_child not in family.step_children:
                    family.step_children.append(step_child)
    def write_individuals(self):
        os.makedirs("output", exist_ok=True)
        filename = os.path.join(
            "output",
            f"individuals_{self.base_gedcom_filename}_{datetime.datetime.now():%Y%b%d}.csv",
        )
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Individual_ID",
                "Individual_Name",
                "Birth_Date",
                "Birth_Place",
                "Death_Date",
                "Death_Place",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for ind in self.individuals.values():
                writer.writerow(
                    dict(
                        Individual_ID=ind.id,
                        Individual_Name=ind.full_name,
                        Birth_Date=ind.birth_date if ind.birth_date else "",
                        Birth_Place=ind.birth_place if ind.birth_place else "",
                        Death_Date=ind.death_date if ind.death_date else "",
                        Death_Place=ind.death_place if ind.birth_place else "",
                    )
                )

    def write_families(self):
        os.makedirs("output", exist_ok=True)
        filename = os.path.join(
            "output",
            f"families_{self.base_gedcom_filename}_{datetime.datetime.now():%Y%b%d}.csv",
        )
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Family_ID",
                "Husband_ID",
                "Husband_Name",
                "Wife_ID",
                "Wife_Name",
                "Marriage_Date",
                "Child_ID",
                "Step_Child_ID",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for family in self.families.values():
                max_length = max(len(family.children), len(family.step_children))
                for i in range(max_length):
                    row = {
                        "Family_ID": family.id,
                        "Husband_ID": family.husband_id,
                        "Husband_Name": family.husband_name,
                        "Wife_ID": family.wife_id,
                        "Wife_Name": family.wife_name,
                        "Marriage_Date": family.marr_date,
                        "Child_ID": family.children[i].id if i < len(family.children) else "",
                        "Step_Child_ID": family.step_children[i].id if i < len(family.step_children) else "",
                    }
                    writer.writerow(row)

    def write_lineage_map(self):
        os.makedirs("output", exist_ok=True)
        lineage = []
        for fam_id, fam in self.families.items():
            for child in fam.children:
                lineage.append(
                    {
                        "Individual_ID": child.id,
                        "Individual_Name": child.name if child.name else "Unknown",
                        "Father_ID": fam.husband_id,
                        "Father_Name": fam.husband_name if fam.husband_name else "Unknown",
                        "Mother_ID": fam.wife_id,
                        "Mother_Name": fam.wife_name if fam.wife_name else "Unknown",
                    }
                )

        filename = os.path.join(
            "output",
            f"lineage_map_{self.base_gedcom_filename}_{datetime.datetime.now():%Y%b%d}.csv",
        )
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Individual_ID",
                "Individual_Name",
                "Father_ID",
                "Father_Name",
                "Mother_ID",
                "Mother_Name",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in lineage:
                writer.writerow(row)