def url_safe(label:str) -> str:
    return (label.
            replace(' ', '').
            replace('&', '_').
            replace('ü', 'ue').
            replace('ä', 'ae').
            replace('ö', 'oe')
            .lower())
