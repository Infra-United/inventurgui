from functools import wraps
from typing import Any, Callable

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n

type colSettings = dict[str, str]
type colDefFunction = Callable[[colSettings, bool, bool], dict[str, Any]]

def col_defs(cart:bool, admin:bool, columns=settings.columns) -> list[dict[str, Any]]:
    return [fn(columns, cart, admin) for fn in col_fns.values()]

col_fns = {}

def register_column(name: str) -> Callable[[colDefFunction], colDefFunction]:
    def decorator(func: colDefFunction) -> colDefFunction:
        @wraps(func)
        def wrapper(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
            return func(columns, cart, admin)
        col_fns[name] = wrapper
        return wrapper
    return decorator

def default_col_defs() -> dict[str, Any]:
    return {
        "editable": False,
        "suppressSizeToFit": True,
        "sortable": True,
        'lockPinned': True,
        "lockVisible": True,
        "suppressMovable": True,
        "resizable": False,
        "filter": False,
        "floatingFilter": False
    }

@register_column("image")
def image_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return {
        "colId": columns['image'],
        "editable": False,
        ":cellRenderer": f'''(p) => p.data.{columns['image']} ?
         "<span class='material-icons-outlined' style='font-size:28px'>info</span>" :
          "<span class='material-icons-outlined' style='font-size:28px'>camera_alt</span>"'''
        if admin else f'''(p) => p.data.{columns['image']} || p.data.{columns['comment']} || p.data.{columns['url']} ? 
        "<span class='material-icons-outlined bg-secondary text-3xl' >info</span>" : null''',
        "hide": cart,
        "maxWidth": 50,
    }

@register_column("object")
def object_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return  {
        "field": columns["object"],
        "filter": not cart,
        "wrapText": True,
        "autoHeight": True,
        "floatingFilter": not cart,
        "sort": "asc" if not cart else '',
        "cellClassRules": {"text-primary": "x", "text-bold": "x", "tracking-wider": "x"}
        if not cart
        else {"text-bold": "x", "tracking-wider": "x"},
    }

# Not used at the moment
def description_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return  {
        "colId": columns["type"],
        "field": columns["type"],
        "suppressSizeToFit": False,
        "wrapText": True,
        "autoHeight": True,
        'sortable': False}

@register_column("weight")
def weight_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return {
            "field": columns["weight"],
            ":valueFormatter": f"(p) => p.value != null ? Math.round(p.value) + ' kg' : null",
            # ":comparator": f'(a, b) => (a == {np.inf}) ? -1 : a - b',
            #":colId": f"(p) => p.data.{config['weight']}.reduce((acc, x) => acc + (x || 0), 0);",
            #":headerValueGetter": f"(p) => p.location === 'header' ? p.column.colId : null;",
            "headerName": f"[kg/{columns["pack"]}]",
            "cellDataType": "number",
    }

@register_column("count")
def count_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return {
            "field": columns["count"],
            ":valueFormatter": f"(p) => p.data.{i18n.get('cart.of')} > 1 ? p.value + ' {i18n.get('cart.of')} ' "
                               f"+ p.data.{i18n.get('cart.of')} : p.value" if cart else "",
            "headerName": "",
            "editable": cart or admin,
            "cellDataType": "number",
            "maxWidth": 80 if not cart else None,
            "lockPosition": "left" if cart else "",
            "sort": "desc" if cart else "",
            "cellClassRules": {"bg-accent": f"data.{i18n.get('cart.of')} > 1",
                               "text-bold": f"data.{i18n.get('cart.of')} > 1"} if cart else "",
        }

@register_column("pack")
def pack_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return {"field": columns["pack"], "lockPosition": "left" if cart else "", 'sortable': False}

# Not Used at the moment
def delete_col() -> dict[str, Any]:
    return {
            "colId": 'add_delete',
            #":editable": f"(p) => p.node.rowPinned ? true : false",
            ":valueGetter": f"(p) => p.node.rowPinned ? 'added' : 'deleted'",
            ":cellRenderer": f'''(p) => p.node.rowPinned ?
                 "<span class='material-icons-outlined' style='font-size:28px'>add</span>" :
                  "<span class='material-icons-outlined' style='font-size:28px'>delete</span>"''',
            "maxWidth": 60
    }

@register_column("total_weight")
def total_weight_col(columns:colSettings, cart:bool, admin:bool) -> dict[str, Any]:
    return {
        "colId": columns["total_weight"],
        "field": columns["total_weight"],
        "cellDataType": "number",
        ":valueFormatter": f"(p) => p.value != null ? Math.round(p.value) + ' kg' : null",
        }
