from typing import Final, Callable

from email_validator import validate_email, EmailNotValidError
from nicegui.observables import ObservableDict

from inventurgui.helper.i18n import i18n

INPUT_VALIDATION: Final[dict[str, Callable[[str], bool]]] = {i18n.get("form.please_fill_field"): lambda v: len(v) > 0}
URL_REGEX: Final[str] = (
    r"(?P<url>https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*))"
)


def validate_mail(key: str, email: str, request: ObservableDict):
    try:
        request.update({key: validate_email(email, check_deliverability=True, strict=True).normalized})
        return None
    except EmailNotValidError as e:
        return e.args[0]

def validate_number(key: str, donation: str, request: ObservableDict):
    try:
        request.update({key: int(donation)})
        return None
    except ValueError:
        return i18n.get("form.number_invalid")