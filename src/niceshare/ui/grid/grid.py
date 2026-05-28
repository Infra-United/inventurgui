from nicegui import ui
from nicegui.elements.aggrid import AgGrid
from nicegui.ui import aggrid
from polars import DataFrame

from niceshare.helper.config import settings
from niceshare.io.cache import Cache
from niceshare.ui.grid.grid_handlers import handle_select
from niceshare.ui.grid.options import options

"""This module implements functions to create AG Grids which display the data."""

columns = settings.columns

@ui.refreshable
async def create_aggrid(name: str, df: DataFrame, cart: bool = False) -> AgGrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        category (str): name of the Category to display
        warehouse (Selection): The warehouse the category belongs to.
        cart (bool): Whether the grid is for the cart page. Defaults to False.

    Returns:
        AgGrid: The AG Grid that results from the given Arguments.
    """
    # Styling
    def background(color: str):
        return f"""{{background-color: {settings.theme[color]}}}"""

    ui.add_body_html(f"<style>.ag-row-selected .ag-cell  {background('secondary')}</style>")
    ui.add_body_html(f"<style>.ag-row-hover .ag-cell  {background('accent')}</style>")
    ui.add_body_html(f"<style>.ag-row-pinned .ag-cell  {background('secondary')}</style>")

    # Create Grid with given Data
    grid = aggrid.from_polars(df, options=options(cart), html_columns=[0], theme="alpine").classes("h-dvh")
    register_event_handlers(grid, name, df, cart)
    return grid


def register_event_handlers(grid: AgGrid, name: str, df: DataFrame, cart: bool):
    """Register the event handlers for the given grid."""
    # Handle events
    grid.on("rowSelected", lambda e: handle_select(e, grid))
    if not cart:
        for row in Cache.selected():
            grid.on("firstDataRendered", lambda r=row: grid.run_row_method(r, "setSelected", True))
    grid.on("gridReady", lambda: grid.run_grid_method("sizeColumnsToFit"), trailing_events=True)
