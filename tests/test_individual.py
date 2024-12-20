from kinship.individual import Individual


def test_individual_initialization():
    ind = Individual(
        "I1", "John Doe", "1990-01-01", "New York", "2020-01-01", "Los Angeles"
    )
    assert ind.id == "I1"
    assert ind.birth_date == "1990-01-01"
    assert ind.birth_place == "New York"
    assert ind.full_name == "John Doe"
    assert ind.death_date == "2020-01-01"
    assert ind.death_place == "Los Angeles"
