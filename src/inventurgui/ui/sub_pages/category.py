from nicegui import ui
from nicegui.elements.drawer import RightDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid.grid import create_aggrid
from inventurgui.ui.helper.reusable_elements import next_fab


async def category_page(category: str | None, warehouse: Warehouse, rd: RightDrawer|None) -> None:
    rd.hide() if rd else None
    path = f"{warehouse.name}/{category}" if category else warehouse.name
    ui.page_title(path)
    LOGGER.debug(f"Creating Grid for {path}...")
    await create_aggrid(warehouse, category, cart=False)
    next_fab(settings.cart)
    LOGGER.info(f"Created Grid for: {path}")
