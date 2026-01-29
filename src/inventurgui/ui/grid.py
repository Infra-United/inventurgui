import pandas
from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.ui import aggrid
from pandas import DataFrame

from inventurgui.helper.config import load_config
from inventurgui.helper.grid_handlers import handle_edit, handle_select
from inventurgui.ui.auth import authenticate_user

"""This module implements functions to create AG Grids which display the data."""

def create_aggrid(name: str, df: DataFrame, cart: bool = False) -> AgGrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        name (str): name of the AG Grid to display
        df (DataFrame): The data to be displayed as a pandas DataFrame.
        cart (bool): Whether the grid is for the cart page. Defaults to False.

    Returns:
        aggrid: The AG Grid that results from the given Arguments.
    """
    # Define Columns for AG Grids
    config = load_config()["data"]

    column_defs = [
        {
            "field": config["object"],
            "filter": not cart,
            "wrapText": True,
            "autoHeight": True,
            "floatingFilter": not cart,
            "sort": "asc" if not cart else '',
            "suppressSizeToFit": False,
            "cellClassRules": {"text-primary": "x", "text-bold": "x", "tracking-wider": "x"}
            if not cart
            else {"text-bold": "x", "tracking-wider": "x"},
        },
        {"field": config["desc"], "wrapText": True, "autoHeight": True, 'sortable': False},
        {
            ":valueGetter": f"(p) => p.data.{config['weight']} ? p.data.{config['weight']} * p.data.{config['count']} : null"
            if cart else f"(p) => p.data.{config['weight']}",
            ":valueFormatter": f"(p) => p.value != null ? Math.round(p.value) + ' kg' : null",
            # ":comparator": f'(a, b) => (a == {np.inf}) ? -1 : a - b',
            #":colId": f"(p) => p.data.{config['weight']}.reduce((acc, x) => acc + (x || 0), 0);",
            #":headerValueGetter": f"(p) => p.location === 'header' ? p.column.colId : null;",
            "headerName": config["total_weight"] + f"" if cart else f"[kg/{config["pack"]}]",
            "cellDataType": "number",
            "suppressSizeToFit": True,
        },
        {
            "field": config["count"],
            ":valueFormatter": f"(p) => p.data.total > 1 ? p.value + ' {config.get('of_total')} ' + p.data.total : p.value" if cart else "",
            #":valueGetter": f"(p) => (p.data.{data["count"]} == 1000) ? 100 : p.data.{data["count"]};",
            #":comparator": f'(a, b) => (a == {np.inf}) ? -1 : a - b',
            "headerName": "",
            "editable": cart,
            "cellDataType": "number",
            "suppressSizeToFit": True,
            "maxWidth": 50 if not cart else None,
            "lockPosition": "left" if cart else "",
            "sort": "desc" if cart else "",
            "cellClassRules": {"bg-accent": "data.total > 1", "text-bold": "data.total > 1"} if cart else "",
        },
        {"field": config["pack"], "lockPosition": "left" if cart else "", "suppressSizeToFit":True, 'sortable': False},
    ]
    default_col_def: dict = {"sortable": True, 'lockPinned': True, "lockVisible":True, "suppressMovable": True, "resizable": False, "filter": False, "floatingFilter": False}

    if config["links"]["display"]:
        # Function to replace https links with HTML string
        def replace_https_with_html(link):
            if pandas.isna(link):
                return link  # Return NaN as is
            if link.startswith("http"):
                return '<span style="font-size: 24px;">ℹ️</span>'
            return link  # Return the link as is if it doesn't start with https://

        # Apply the function to the 'links' column
        pandas.options.mode.copy_on_write = True
        config["has_link"] = df[config["links"]["column"]].apply(replace_https_with_html)
        link_column = {"headerName": "", "field": "has_link", "filter": False, "minWidth": 50, "maxWidth": 50}
        column_defs.insert(0, link_column)

    # Styling
    # height = 'h-[calc(100vh-56px)]' if not cart else 'h-[calc(100vh-104px)]'
    theme = app.storage.user["grid_theme"] if app.storage.user.get("grid_theme") else "alpine"
    def background(color:str):
        return f"""{{background-color: {load_config()["theme"][color]}}}"""
    ui.add_body_html(f"<style>.ag-row-selected .ag-cell  {background('secondary')}</style>")
    ui.add_body_html(f"<style>.ag-row-hover .ag-cell  {background('accent')}</style>")

    # Create Grid with given Data
    grid = aggrid(
        {
            "selectionColumnDef": {"hide": cart, "maxWidth": 35, "sortable": True},
            "columnDefs": column_defs,
            "defaultColDef": default_col_def,
            "rowData": (df.to_dict("records")),
            "theme": theme,
            "alwaysMultiSort": True,
            "rowSelection": {
                "mode": "multiRow",
                "selectAll": "filtered",
                "ctrlASelectsRows": True,
                "enableClickSelection": True,
                "checkboxes": True,
                "headerCheckbox": True,
                "enableSelectionWithoutKeys": True,
            }
            if not cart
            else "",
            "autoSizeStrategy": {
                'type': 'fitCellContents',
                'animateColumnResizing': True,
                'skipHeaderOnAutoSize': True,
                'scaleUpToFitGridWidth': True,
            },
            "suppressRowHoverHighlight": cart,
            "enterNavigatesVertically": True,
            "readOnlyEdit": True,
            "invalidEditValueMode": "block",
            "stopEditingWhenCellsLoseFocus": True,
            "suppressCellFocus": True,
            "enterNavigatesVerticallyAfterEdit": True,
            "singleClickEdit": True,
            ":getRowId": "(params) => params.data.perma_id.toString()",
        },
        html_columns=[0],
        theme=theme,
    ).classes("h-dvh w-full")

    # Handle events
    grid.on("rowSelected", lambda event: handle_select(name, event))
    if not cart:
        for row in app.storage.user[name]:
            grid.on("firstDataRendered", lambda r=row: grid.run_row_method(r, "setSelected", True))
    else:
        for row in app.storage.user["amounts"].get(name, name):
            grid.on(
                "firstDataRendered",
                lambda r=row: grid.run_row_method(
                    r, "setDataValue", config["count"], app.storage.user["amounts"].get(name, name).get(r)[0]
                ),
            )
    grid.on("cellEditRequest", lambda event: handle_edit(grid, name, event))
    grid.on("gridSizeChanged", lambda: grid.run_grid_method("autoSizeAllColumns"), leading_events=True)
    grid.on("gridSizeChanged", lambda: grid.run_grid_method("sizeColumnsToFit" if int(app.storage.user['screen'].get('width')) > 640 else 'None'), leading_events=True)
    return grid


def dialog(event_args: dict):
    with ui.dialog() as dia:
        with ui.card():
            ui.label(text=f"{event_args['data']['Objekt']} ({event_args['data']['Art']})")
            ui.image(event_args["data"]["Link"])
    return dia
