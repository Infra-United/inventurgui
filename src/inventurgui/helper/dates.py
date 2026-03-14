import datetime
from typing import Tuple

from inventurgui.helper.config import settings


def convert_dates(dates: str | dict[str, str]) -> Tuple[str, str, str, str]:
    """
    Converts the dates supplied from a date_range_picker to the configured format.
    Also returns the month (%B) and year (%y) of the range.
    See https://strftime.org/ for more information.
    :param dates: {'from': start, 'to': end}
    :return: start, end, month, year
    """
    if isinstance(dates, dict):
        start = dates.get("from")
        end = dates.get("to")
    else:
        start = dates
        end = dates
    start = datetime.date.fromisoformat(start)
    end = datetime.date.fromisoformat(end)
    year = f"{start:%y}/{end:%y}" if not start.year == end.year else f"{start:%y}"
    month = f"{start:%B}/{end:%B}" if not start.month == end.month else f"{start:%B}"
    start = start.strftime(settings.date_format)
    end = end.strftime(settings.date_format)
    return start, end, month, year
