from contextlib import suppress

# TODO replace with slugify?

def url_safe(label: str) -> str:
    with suppress(AttributeError):
        return label.replace(" ", "").replace("&", "_").replace("ü", "ue").replace("ä", "ae").replace("ö", "oe").lower()
    return ""

def reverse_url(url: str) -> str:
    return url.replace("_", " & ").replace("ue", "ü").replace("ae", "ä").replace("oe", "ö").title()
