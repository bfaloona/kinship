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

