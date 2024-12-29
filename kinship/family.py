from typing import List
from .util import normalize_id, date_string
from .individual import Individual

class Family:
    def __init__(
        self,
        id: str,
        husband_id=None,
        husband_name=None,
        wife_id=None,
        wife_name=None,
        marr_date: str = None,
        children: List[Individual] = None,
    ):
        self.id = normalize_id(id)
        self.husband_name = husband_name if husband_name else None
        self.husband_id = husband_id if husband_id else None
        self.wife_name = wife_name if wife_name else None
        self.wife_id = wife_id if wife_id else None
        self.marr_date = date_string(marr_date)
        self.children = children if children else []

    def get_parents(self) -> List[str]:
        """
        Return a list of parent IDs (husband_id and wife_id).
        """
        parents = []
        if self.husband_id:
            parents.append(self.husband_id)
        if self.wife_id:
            parents.append(self.wife_id)
        return parents

    def __str__(self):
        return f"Family: {self.id}\n{self.husband_name} ({self.husband_id}) + {self.wife_name} ({self.wife_id}) m{self.marr_date}\n{self.children}\n"
