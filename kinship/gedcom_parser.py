import os
import csv
import datetime
from typing import Dict, Set
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

    def parse_individual(self, individual):
        try:
            name = individual.name.format()
        except AttributeError:
            name = individual.sub_tag_value("NAME") or "Unknown"
        sex = individual.sex
        birth_date = individual.sub_tag_value("BIRT/DATE")
        birth_place = individual.sub_tag_value("BIRT/PLAC")
        death_date = individual.sub_tag_value("DEAT/DATE")
        death_place = individual.sub_tag_value("DEAT/PLAC")
        ind = Individual(
            normalize_id(individual.xref_id), name, sex, birth_date, birth_place, death_date, death_place
        )
        self.individuals[ind.id] = ind

    def parse_family(self, family):
        husband = family.sub_tag("HUSB")
        wife = family.sub_tag("WIFE")
        children_records = family.sub_tags("CHIL")
        marr_date = family.sub_tag_value("MARR/DATE")  # Ensure it's a single value
        children = [normalize_id(child.xref_id) for child in children_records]
        if husband and normalize_id(husband.xref_id) not in self.individuals:
            raise ValueError(
                f"Warning: Husband ID {husband.xref_id} not found in individuals list."
            )
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
                "Sex",
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
                        Sex=ind.sex,
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
                        "Child_ID": family.children[i] if i < len(family.children) else ""
                    }
                    writer.writerow(row)

    def get_individuals(self):
        return self.individuals

    def get_families(self):
        return self.families
