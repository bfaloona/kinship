
def normalize_id(xref_id: str) -> str:
    return xref_id.replace("@", "")

def date_string(date):
    if not date:
        return ""

    try:
        return date[0].value.date
    except (AttributeError, IndexError, TypeError):
        pass

    try:
        return date.value.date
    except AttributeError:
        pass

    try:
        return str(date)
    except Exception:
        pass

    return ""


def display(individuals, content) -> str:
    """Pretty Print content depending on the type"""
    from kinship.family import Family
    from kinship.individual import Individual

    result = content
    if content is None:
        result = "None"

    elif isinstance(content, list):
        if not content:
            result = "list[]"
        elif isinstance(content[0], Individual) or \
                isinstance(content[0], Family):
            result = "\n".join([display(individuals, ind) for ind in content])

    elif isinstance(content, set):
        if not content:
            result = "set()"
        else:
            result = "\n".join([display(individuals, item) for item in content])

    elif isinstance(content, dict):
        if not content:
            result = "dict{}"
        else:
            result = "\n".join([f"{k}: {display(individuals, v)}" for k, v in content.items()])

    elif isinstance(content, str):
        if content in individuals:
            result = display(individuals, individuals[content])
        else:
            result = content

    elif isinstance(content, Individual):
        result = f"{content.full_name} ({content.id})"

    elif isinstance(content, Family):
        fam = content
        result = f"Family: {fam.id}\n{display(individuals, fam.husband_id)} + {display(individuals, fam.wife_id)} M:{fam.marr_date}\n{display(individuals, fam.children)}\n"

    return result