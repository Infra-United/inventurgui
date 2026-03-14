import polars as pl
from nicegui import ui
from nicegui.elements.aggrid import AgGrid
from nicegui.ui import aggrid
from polars import DataFrame

from inventurgui.helper.config import settings
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.grid.grid_handlers import handle_select, handle_click, update_amount
from inventurgui.ui.grid.options import options

"""This module implements functions to create AG Grids which display the data."""

columns = settings.columns

def create_aggrid(warehouse: Warehouse, category:str|None = None, cart: bool = False) -> AgGrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        category (str): name of the Category to display
        warehouse (Warehouse): The warehouse the category belongs to.
        cart (bool): Whether the grid is for the cart page. Defaults to False.

    Returns:
        AgGrid: The AG Grid that results from the given Arguments.
    """
    admin = authenticate_user()

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
        df = warehouse.inventory.filter(pl.col(columns["category"]) == category)

    # Create Grid with given Data
    grid = aggrid.from_polars(df, options=options(cart, admin), html_columns=[0],  theme='alpine').classes("h-dvh")
    #grid.options.update({"pinnedBottomRowData": f"[Gesamtgewicht: {warehouse.total_weight()}]"})

    register_event_handlers(grid, warehouse.name, df, cart, admin)
    return grid

def register_event_handlers(grid: AgGrid, name:str, df:DataFrame, cart:bool, admin:bool):
    """Register the event handlers for the given grid."""
    # Handle events
    grid.on("rowSelected", lambda e: handle_select(name, e, grid))
    if not cart:
        grid.on("cellClicked", lambda event: handle_click(name, grid, event, df))
        if not admin:
            for row in Cache.selected(name):
                grid.on("firstDataRendered", lambda r=row: grid.run_row_method(r, "setSelected", True))
    if cart:
        for row, value in Cache.amounts(name).items():
            grid.on("firstDataRendered", lambda r=row: grid.run_row_method(r, "setDataValue", columns["count"], value))
        grid.on("cellEditRequest", lambda event: update_amount(grid, name, event))

    grid.on("gridSizeChanged", lambda: grid.run_grid_method("autoSizeAllColumns"), trailing_events=True)
    # ui.on('resize', lambda e: grid.run_grid_method("sizeColumnsToFit") if e.args['width'] > 768 else None, trailing_events=True)