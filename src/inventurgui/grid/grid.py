from nicegui import ui
from nicegui.elements.aggrid import AgGrid
from nicegui.ui import aggrid

from inventurgui.grid.columns import default_column_options, col_fns
from inventurgui.helper.config import settings
from inventurgui.grid.grid_handlers import handle_select, handle_click, update_amount
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user

"""This module implements functions to create AG Grids which display the data."""


def create_aggrid(warehouse: Warehouse, category:str|None = None, cart: bool = False) -> AgGrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        category (str): name of the Category to display
        warehouse (Warehouse): The warehouse the category belongs to.
        cart (bool): Whether the grid is for the cart page. Defaults to False.

    Returns:
        AgGrid: The AG Grid that results from the given Arguments.
    """
    # Define Columns for AG Grids
    columns = settings.columns
    admin = authenticate_user()

    col_defs = [col_fns.get(c)(columns, cart, admin) if col_fns.get(c) else {"hide":True} for c in columns.keys()]

    # Styling
    def background(color: str):
        return f"""{{background-color: {settings.theme[color]}}}"""

    ui.add_body_html(f"<style>.ag-row-selected .ag-cell  {background('secondary')}</style>")
    ui.add_body_html(f"<style>.ag-row-hover .ag-cell  {background('accent')}</style>")
    ui.add_body_html(f"<style>.ag-row-pinned .ag-cell  {background('secondary')}</style>")

    # Data
    if category == settings.warehouse.get("everything"):
        df = warehouse.inventory
    elif category == settings.warehouse.get("selection") or category is None and cart:
        df = warehouse.selected()
    else:
        df = warehouse.inventory[warehouse.inventory[settings.columns["category"]] == category]

    # Create Grid with given Data
    grid = aggrid(
        {
            "selectionColumnDef": {"hide": cart, "maxWidth": 35, "sortable": True},
            "columnDefs": col_defs,
            "defaultColDef": default_column_options(admin),
            "rowData": (df.to_dict("records")),
            "alwaysMultiSort": True,
            "rowSelection": {
                "mode": "multiRow",
                "selectAll": "filtered",
                "checkboxes": True,
                "headerCheckbox": True,
            }
            if not cart and not admin
            else "",
            "autoSizeStrategy": {
                'type': 'fitCellContents',
                'scaleUpToFitGridWidth': True,
            },
            "suppressRowHoverHighlight": cart,
            "undoRedoCellEditing": True,
            "undoRedoCellEditingLimit": 20,
            "readOnlyEdit": not admin,
            "invalidEditValueMode": "block" if not admin else "",
            "suppressCellFocus": not admin,
            "enterNavigatesVerticallyAfterEdit": True,
            "singleClickEdit": True,
            "stopEditingWhenCellsLoseFocus": True,
            ":getRowId": "p.data.perma_id.toString()",
        },
        html_columns=[0],
        theme='alpine',
        modules="community"
    ).classes("h-dvh w-full")

    # Handle events
    grid.on("rowSelected",lambda e: handle_select(warehouse.name, e, grid))
    if not cart:
        grid.on("cellClicked", lambda event: handle_click(warehouse.name, grid, event, df))
        if not admin:
            for row in Cache.selected(warehouse.name):
                grid.on("firstDataRendered", lambda r=row: grid.run_row_method(r, "setSelected", True))
    if cart:
        for row in Cache.amounts().get(warehouse.name):
            grid.on(
                "firstDataRendered",
                lambda r=row: grid.run_row_method(
                    r, "setDataValue", columns["count"], Cache.amounts().get(warehouse.name).get(r)[0]
                ),
            )
        grid.on("cellEditRequest", lambda event: update_amount(grid, warehouse.name, event))

    grid.on("gridSizeChanged", lambda: grid.run_grid_method("autoSizeAllColumns"), trailing_events=True)
    #ui.on('resize', lambda e: grid.run_grid_method("sizeColumnsToFit") if e.args['width'] > 768 else None, trailing_events=True)
    return grid