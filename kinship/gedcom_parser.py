import os
import csv
import datetime
from typing import Dict, Set
from itertools import combinations
from ged4py.parser import GedcomReader

from .individual import Individual
from .family import Family
from .util import normalize_id


class GedcomParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.base_gedcom_filename = os.path.splitext(os.path.basename(file_path))[0]
        self.individuals: Dict[str, Individual] = {}
        self.families: Dict[str, Family] = {}
        self.relationships = []
        self.child_to_parents: Dict[str, Set[str]] = {}
        self.parent_to_children: Dict[str, Set[str]] = {}
        self.parent_to_step_children: Dict[str, Set[str]] = {}

    def parse_gedcom_file(self):
        with GedcomReader(self.file_path) as ged_parser:
            for individual in ged_parser.records0("INDI"):
                self.parse_individual(individual)
            for family in ged_parser.records0("FAM"):
                fam = self.parse_family(family)
                for child in self.families[fam.id].children:
                    self.child_to_parents[child.id] = {fam.husband_id, fam.wife_id}
        self.parent_to_children = create_parent_to_children(self.families)
        self.parent_to_step_children = create_parent_to_step_children(self.families, self.parent_to_children)

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
        children = [self.individuals[normalize_id(child.xref_id)] for child in children_records]
        if husband and normalize_id(husband.xref_id) not in self.individuals:
            raise ValueError(
                f"Warning: Husband ID {husband.xref_id} not found in individuals list."
            )
        if wife and normalize_id(wife.xref_id) not in self.individuals:
            # raise ValueError(f"Warning: Wife ID {wife.xref_id} not found in individuals list.")
            pass
        if not husband and not wife:
            # raise ValueError("Warning: Family has no husband or wife.")
            pass
        fam = Family(
            normalize_id(family.xref_id),
            normalize_id(husband.xref_id) if husband else None,
            husband.name.format() if husband else None,
            normalize_id(wife.xref_id) if wife else None,
            wife.name.format() if wife else None,
            marr_date if marr_date else None,
            children
        )
        self.families[fam.id] = fam
        return fam

    def add_step_child_to_parent(self, child_id, parent_id):
        if parent_id not in self.parent_to_step_children:
            self.parent_to_step_children[parent_id] = set()
        self.parent_to_step_children[parent_id].add(child_id)

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
                "Child_ID"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for family in self.families.values():
                for i in range(len(family.children)):
                    row = {
                        "Family_ID": family.id,
                        "Husband_ID": family.husband_id,
                        "Husband_Name": family.husband_name,
                        "Wife_ID": family.wife_id,
                        "Wife_Name": family.wife_name,
                        "Marriage_Date": family.marr_date,
                        "Child_ID": family.children[i].id if i < len(family.children) else ""
                    }
                    writer.writerow(row)


    def get_relationships(self):
        """
        Generate and return the network graph as a list of dictionaries without saving to disk.
        """
        if len(self.relationships) > 0:
            return self.relationships

        if not self.individuals or not self.families:
            raise ValueError("Parser has not loaded individuals or families. Ensure parse() is called.")

        # Add parent-child relationships
        for family in self.families.values():
            for child in family.children:
                if family.husband_id != "Unknown":
                    self.relationships.append({
                        "Source": family.husband_id,
                        "Target": child.id,
                        "Relationship": "parent-child"
                    })
                if family.wife_id != "Unknown":
                    self.relationships.append({
                        "Source": family.wife_id,
                        "Target": child.id,
                        "Relationship": "parent-child"
                    })

        # Add spousal relationships
        for family in self.families.values():
            if family.husband_name != "Unknown" and family.wife_name != "Unknown":
                self.relationships.append({
                    "Source": family.husband_id,
                    "Target": family.wife_id,
                    "Relationship": "spouse"
                })
                self.relationships.append({
                    "Source": family.wife_id,
                    "Target": family.husband_id,
                    "Relationship": "spouse"
                })

        # Add sibling relationships
        for family in self.families.values():
            child_ids = [child.id for child in family.children]
            sibling_pairs = combinations(child_ids, 2)
            for sibling1, sibling2 in sibling_pairs:
                self.relationships.append({
                    "Source": sibling1,
                    "Target": sibling2,
                    "Relationship": "sibling"
                })
                self.relationships.append({
                    "Source": sibling2,
                    "Target": sibling1,
                    "Relationship": "sibling"
                })

        # Add step-parent relationships
        all_spouses = set()
        for family in self.families.values():
            all_spouses.add(family.husband_id)
            all_spouses.add(family.wife_id)

        for spouse_id in all_spouses:
            if spouse_id in self.parent_to_step_children:
                for child_id in self.parent_to_step_children[spouse_id]:
                    self.relationships.append({
                        "Source": spouse_id,
                        "Target": child_id,
                        "Relationship": "step-parent"
                    })

        return self.relationships

    def write_relationships(self, relationships=None):
        """
        Generate a CSV representing the family tree network graph data,
        including step-parent relationships. Optionally accepts a precomputed
        network map from get_relationships().
        """
        # Ensure parser has parsed the data
        if not self.individuals or not self.families:
            raise ValueError("Parser has not loaded individuals or families. Ensure parse() is called.")

        if relationships is None:
            relationships = self.get_relationships()

        filename = os.path.join(
            "output",
            f"relationships_{self.base_gedcom_filename}_{datetime.datetime.now():%Y%b%d}.csv",
        )

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Source", "Target", "Relationship"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for entry in relationships:
                writer.writerow(entry)

    def get_individuals(self):
        return self.individuals

    def get_families(self):
        return self.families


def create_parent_to_children(families: dict[str, Family]) -> dict[str, Set[str]]:
    parent_to_children = {}
    for family in families.values():
        for parent_id in [family.husband_id, family.wife_id]:
            if parent_id not in parent_to_children:
                parent_to_children[parent_id] = set()
            for child in family.children:
                parent_to_children[parent_id].add(child.id)
    return parent_to_children

def create_parent_to_step_children(families: dict[str, Family], parent_to_children: dict[str, Set[str]]) -> dict[
    str, Set[str]]:
    parent_to_step_children = {}

    for family in families.values():
        # Biological children in the current family
        family_biological_children = set(child.id for child in family.children)

        # Husband: Add wife's other children
        for child_id in parent_to_children.get(family.wife_id, set()):
            if child_id not in family_biological_children and \
                    child_id not in parent_to_children.get(family.husband_id, set()):
                parent_to_step_children.setdefault(family.husband_id, set()).add(child_id)

        # Wife: Add husband's other children
        for child_id in parent_to_children.get(family.husband_id, set()):
            if child_id not in family_biological_children and \
                    child_id not in parent_to_children.get(family.wife_id, set()):
                parent_to_step_children.setdefault(family.wife_id, set()).add(child_id)

    return parent_to_step_children
