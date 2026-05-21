from functools import wraps
from typing import Any, Callable

from dataviewer.helper.config import settings

type colSettings = dict[str, str]
type colDefFunction = Callable[[colSettings, bool], dict[str, Any]]


def col_defs(cart: bool, columns=settings.columns) -> list[dict[str, Any]]:
    return [col_fns.get(c)(columns, cart) if col_fns.get(c) else {"hide": True} for c in columns.keys()]


col_fns = {}


def register_column(name: str) -> Callable[[colDefFunction], colDefFunction]:
    def decorator(func: colDefFunction) -> colDefFunction:
        @wraps(func)
        def wrapper(columns: colSettings, cart: bool) -> dict[str, Any]:
            return func(columns, cart)

        col_fns[name] = wrapper
        return wrapper

    return decorator


def default_col_defs() -> dict[str, Any]:
    return {
        "editable": False,
        "suppressSizeToFit": True,
        "sortable": True,
        "lockPinned": True,
        "lockVisible": True,
        "suppressMovable": True,
        "resizable": False,
        "filter": False,
        "floatingFilter": False,
    }


@register_column("url")
def image_col(columns: colSettings, cart: bool) -> dict[str, Any]:
    return {
        "colId": columns["url"],
        "editable": False,
        ":cellRenderer": f"""(p) => p.data.{columns["dance"]} || p.data.{columns["url"]} ? 
        "<span class='material-icons-outlined bg-secondary text-3xl' >info</span>" : null""",
        "lockPosition": "left",
        "hide": cart,
        "maxWidth": 50,
    }


@register_column("title")
def object_col(columns: colSettings, cart: bool) -> dict[str, Any]:
    return {
        "field": columns["title"],
        "filter": not cart,
        "wrapText": True,
        "autoHeight": True,
        ":suppressSizeToFit": "Quasar.Screen.lt.sm",
        "floatingFilter": not cart,
        "sort": "asc" if not cart else "",
        "cellClassRules": {"text-primary": "x", "text-bold": "x", "tracking-wider": "x"},
    }

@register_column("lyrics")
def description_col(columns: colSettings, cart: bool) -> dict[str, Any]:
    return {
        "field": columns["lyrics"],
        "suppressSizeToFit": False,
        "wrapText": True,
        "autoHeight": False,
        "sortable": False,
    }

@register_column("tone")
def pack_col(columns: colSettings, cart: bool) -> dict[str, Any]:
    return {
        "field": columns["tone"],
        "lockPosition": "left" if cart else "",
        "sortable": False,
        # ":hide": "Quasar.Screen.lt.sm" if not cart else "",
    }


@register_column("chord")
def pack_col(columns: colSettings, cart: bool) -> dict[str, Any]:
    return {
        "field": columns["chord"],
        "lockPosition": "left" if cart else "",
        "sortable": False,
        # ":hide": "Quasar.Screen.lt.sm" if not cart else "",
    }


# Not Used at the moment
def delete_col() -> dict[str, Any]:
    return {
        "colId": "add_delete",
        # ":editable": f"(p) => p.node.rowPinned ? true : false",
        ":valueGetter": "(p) => p.node.rowPinned ? 'added' : 'deleted'",
        ":cellRenderer": '''(p) => p.node.rowPinned ?
                 "<span class='material-icons-outlined' style='font-size:28px'>add</span>" :
                  "<span class='material-icons-outlined' style='font-size:28px'>delete</span>"''',
        "maxWidth": 60,
    }
