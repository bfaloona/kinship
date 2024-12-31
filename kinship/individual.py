class Individual:
    def __init__(self, id, full_name, sex='U', birth_date=None, birth_place=None, death_date=None, death_place=None):
        self.id = id
        self.full_name = full_name
        self.sex = sex
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.death_date = death_date
        self.death_place = death_place

    def __str__(self):
        return f"{self.full_name} ({self.id})"