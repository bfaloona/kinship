from .util import normalize_id


class Child:
    def __init__(self, xref_id, name):
        self.id = normalize_id(xref_id)
        self.name = name