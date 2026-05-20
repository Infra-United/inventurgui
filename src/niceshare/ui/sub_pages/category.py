import polars as pl
from nicegui import ui
from nicegui.elements.drawer import RightDrawer

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.io.warehouse import Warehouse
from niceshare.ui.auth import authenticate_user
from niceshare.ui.grid.grid import create_aggrid
from niceshare.ui.grid.grid_handlers import handle_click
from niceshare.ui.helper.reusable_elements import next_fab, save_fab


async def category_page(category: str | None, warehouse: Warehouse, rd: RightDrawer|None) -> None:
    rd.hide() if rd else None
    path = f"{warehouse.name}/{category}" if category else warehouse.name
    ui.page_title(path)
    LOGGER.debug(f"Creating Grid for {path}...")
    # Data
    if category == warehouse.name:
        df = warehouse.inventory
    elif category == settings.warehouse.get("selection"):
        df = warehouse.selected()
    else:
        df = warehouse.inventory.filter(pl.col(settings.columns["category"]) == category)
    grid = await create_aggrid(warehouse.name, df)
    grid.on("cellClicked", lambda event: handle_click(warehouse, grid, event))
    if authenticate_user():
        save_fab(warehouse)
    else:
        next_fab(settings.cart)
    LOGGER.info(f"Created Grid for: {path}")
