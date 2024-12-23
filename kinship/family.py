from typing import List
from .util import normalize_id, date_string
from .individual import Individual

class Family:
    def __init__(
        self,
        xref_id: str,
        husband=None,
        wife=None,
        marr_date: str = None,
        children: List[Individual] = None,
    ):
        self.id = normalize_id(xref_id)
        self.husband_name = husband.name.format() if husband else "Unknown"
        self.husband_id = normalize_id(husband.xref_id) if husband else "-"
        self.wife_name = wife.name.format() if wife else "Unknown"
        self.wife_id = normalize_id(wife.xref_id) if wife else "-"
        self.marr_date = date_string(marr_date)
        self.children = children if children else []

    def __str__(self):
        return f"Family: {self.id}\n{self.husband_name} ({self.husband_id}) + {self.wife_name} ({self.wife_id}) m{self.marr_date}\n{self.children}\n"
