class Individual:
    def __init__(self, id, full_name, birth_date, birth_place, death_date, death_place):
        self.id = id
        self.full_name = full_name
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.death_date = death_date
        self.death_place = death_place

    def __str__(self):
        return f"{self.full_name} ({self.id})"