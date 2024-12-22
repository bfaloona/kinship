from typing import List
from .child import Child
from .util import normalize_id, date_string

class Family:
    def __init__(
        self,
        xref_id: str,
        husband=None,
        wife=None,
        marr_date: str = None,
        children: List[Child] = None,
        step_children: List[Child] = None,
    ):
        self.id = normalize_id(xref_id)
        self.husband_name = husband.name.format() if husband else "Unknown"
        self.husband_id = normalize_id(husband.xref_id) if husband else "Unknown"
        self.wife_name = wife.name.format() if wife else "Unknown"
        self.wife_id = normalize_id(wife.xref_id) if wife else "Unknown"
        self.marr_date = date_string(marr_date)
        self.children = children if children else []
