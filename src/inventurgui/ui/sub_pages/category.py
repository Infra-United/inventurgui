import polars as pl
from nicegui import ui
from nicegui.elements.drawer import RightDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.grid.grid import create_aggrid
from inventurgui.ui.helper.reusable_elements import next_fab, save_fab


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
    await create_aggrid(warehouse.name, df)
    if authenticate_user():
        save_fab(warehouse)
    else:
        next_fab(settings.cart)
    LOGGER.info(f"Created Grid for: {path}")
