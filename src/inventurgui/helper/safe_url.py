def url_safe(label:str) -> str:
    return (label.
            replace(' ', '').
            replace('&', '_').
            replace('ü', 'ue').
            replace('ä', 'ae').
            replace('ö', 'oe')
            .lower())

def reverse_url(url:str) -> str:
    return (url.
            replace('_', ' & ').
            replace('ue', 'ü').
            replace('ae', 'ä').
            replace('oe', 'ö')
            .title())