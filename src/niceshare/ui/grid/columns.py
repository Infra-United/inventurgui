from functools import wraps
from typing import Any, Callable

from niceshare.helper.config import settings

type colSettings = dict[str, str]
type colDefFunction = Callable[[colSettings, bool, bool], dict[str, Any]]


def col_defs(cart: bool, admin: bool, columns=settings.columns) -> list[dict[str, Any]]:
    return [col_fns.get(c)(columns, cart, admin) if col_fns.get(c) else {"hide": True} for c in columns.keys()]


col_fns = {}


def register_column(name: str) -> Callable[[colDefFunction], colDefFunction]:
    def decorator(func: colDefFunction) -> colDefFunction:
        @wraps(func)
        def wrapper(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
            return func(columns, cart, admin)

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


@register_column("image")
def image_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "colId": columns["image"],
        "editable": False,
        ":cellRenderer": f'''(p) => p.data.{columns["image"]} ?
         "<span class='material-icons-outlined' style='font-size:28px'>image</span>" :
          "<span class='material-icons-outlined' style='font-size:28px'>camera_alt</span>"'''
        if admin
        else f"""(p) => p.data.{columns["image"]} || p.data.{columns["comment"]} || p.data.{columns["url"]} ? 
        "<span class='material-icons-outlined bg-secondary text-3xl' >info</span>" : null""",
        "lockPosition": "left",
        "hide": cart,
        "maxWidth": 50,
    }


@register_column("object")
def object_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "field": columns["object"],
        "filter": not cart,
        "wrapText": True,
        "autoHeight": True,
        ":suppressSizeToFit": "Quasar.Screen.lt.sm",
        "floatingFilter": not cart,
        "sort": "asc" if not cart else "",
        "cellClassRules": {"text-primary": "x", "text-bold": "x", "tracking-wider": "x"},
    }


# Not used at the moment
def description_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "colId": columns["type"],
        "field": columns["type"],
        "suppressSizeToFit": False,
        "wrapText": True,
        "autoHeight": True,
        "sortable": False,
    }


@register_column("weight")
def weight_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "field": columns["weight"],
        ":valueFormatter": "(p) => p.value != null ? p.value + ' kg' : null",
        # ":comparator": f'(a, b) => (a == {np.inf}) ? -1 : a - b',
        # ":colId": f"(p) => p.data.{config['weight']}.reduce((acc, x) => acc + (x || 0), 0);",
        # ":headerValueGetter": f"(p) => p.location === 'header' ? p.column.colId : null;",
        "headerName": f"[kg/{columns['pack']}]",
        "cellDataType": "number",
        ":hide": "Quasar.Screen.lt.sm" if not cart else "",
    }


@register_column("count")
def count_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "colId": columns["count"],
        ":valueGetter": f"(p) => p.data.{columns['count']}",
        ":valueFormatter": f"(p) => p.data.{columns['total']} > 1 ? p.value + ' {columns['total']} ' "
        f"+ p.data.{columns['total']} : p.value"
        if cart
        else "",
        "headerName": "",
        "editable": cart or admin,
        "cellDataType": "number",
        "maxWidth": 80 if not cart else None,
        "lockPosition": "left" if cart else "",
        "sort": "desc" if cart else "",
        "cellClassRules": {"bg-accent": f"data.{columns['total']} > 1", "text-bold": f"data.{columns['total']} > 1"}
        if cart
        else "",
    }


@register_column("pack")
def pack_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "field": columns["pack"],
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


@register_column("total_weight")
def total_weight_col(columns: colSettings, cart: bool, admin: bool) -> dict[str, Any]:
    return {
        "colId": columns["total_weight"],
        "field": columns["total_weight"],
        "cellDataType": "number",
        ":valueFormatter": "(p) => p.value != null ? Math.round(p.value) + ' kg' : null",
        "hide": not cart,
        "cellClassRules": {"text-bold": "x", "tracking-wider": "x"},
    }
