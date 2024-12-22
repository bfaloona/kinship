import os
import csv
import datetime
from typing import Dict, Set
from itertools import combinations
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
        self.child_to_biological_parents: Dict[str, Set[str]] = {}
        self.parent_to_children: Dict[str, Set[str]] = {}
        self.parent_to_step_children: Dict[str, Set[str]] = {}

    def parse(self):
        with GedcomReader(self.file_path) as ged_parser:
            for individual in ged_parser.records0("INDI"):
                self.parse_individual(individual)
            for family in ged_parser.records0("FAM"):
                fam = self.parse_family(family)
                for child in self.families[fam.id].children:
                    self.child_to_biological_parents[child.id] = {fam.husband_id, fam.wife_id}
        self.create_parent_to_children()
        self.create_parent_to_step_children()

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

    def create_parent_to_children(self):
        for family in self.families.values():
            for parent_id in [family.husband_id, family.wife_id]:
                if parent_id not in self.parent_to_children:
                    self.parent_to_children[parent_id] = set()
                for child in family.children:
                    self.parent_to_children[parent_id].add(child.id)

    def create_parent_to_step_children(self):
        """Compare children across families to identify step-children"""
        for family in self.families.values():
            family_biological_children = set(child.id for child in family.children)

            # husband: add wife's other children
            for child_id in self.parent_to_children.get(family.wife_id, set()):
                if child_id not in family_biological_children:
                    self.add_step_child_to_parent(child_id, family.husband_id)

            # wife: add husband's other children
            for child_id in self.parent_to_children.get(family.husband_id, set()):
                if child_id not in family_biological_children:
                    self.add_step_child_to_parent(child_id, family.wife_id)

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

    def get_network_graph(self):
        """
        Generate and return the network graph as a list of dictionaries without saving to disk.
        """
        if not self.individuals or not self.families:
            raise ValueError("Parser has not loaded individuals or families. Ensure parse() is called.")

        network_map = []

        # Add parent-child relationships
        for family in self.families.values():
            for child in family.children:
                if family.husband_id != "Unknown":
                    network_map.append({
                        "Source": family.husband_id,
                        "Target": child.id,
                        "Relationship": "parent-child"
                    })
                if family.wife_id != "Unknown":
                    network_map.append({
                        "Source": family.wife_id,
                        "Target": child.id,
                        "Relationship": "parent-child"
                    })

        # Add spousal relationships
        for family in self.families.values():
            if family.husband_name != "Unknown" and family.wife_name != "Unknown":
                network_map.append({
                    "Source": family.husband_id,
                    "Target": family.wife_id,
                    "Relationship": "spouse"
                })
                network_map.append({
                    "Source": family.wife_id,
                    "Target": family.husband_id,
                    "Relationship": "spouse"
                })

        # Add sibling relationships
        for family in self.families.values():
            child_ids = [child.id for child in family.children]
            sibling_pairs = combinations(child_ids, 2)
            for sibling1, sibling2 in sibling_pairs:
                network_map.append({
                    "Source": sibling1,
                    "Target": sibling2,
                    "Relationship": "sibling"
                })
                network_map.append({
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
                    network_map.append({
                        "Source": spouse_id,
                        "Target": child_id,
                        "Relationship": "step-parent"
                    })

        return network_map

    def write_network_graph(self, network_map=None):
        """
        Generate a CSV representing the family tree network graph data,
        including step-parent relationships. Optionally accepts a precomputed
        network map from get_network_graph().
        """
        # Ensure parser has parsed the data
        if not self.individuals or not self.families:
            raise ValueError("Parser has not loaded individuals or families. Ensure parse() is called.")

        if network_map is None:
            network_map = self.get_network_graph()

        filename = os.path.join(
            "output",
            f"network_graph_{self.base_gedcom_filename}_{datetime.datetime.now():%Y%b%d}.csv",
        )

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Source", "Target", "Relationship"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for entry in network_map:
                writer.writerow(entry)

    def get_individuals(self):
        return self.individuals

    def get_families(self):
        return self.families
