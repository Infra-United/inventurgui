from nicegui import ui
from nicegui.elements.drawer import LeftDrawer, RightDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid.grid import create_aggrid
from inventurgui.ui.helper.reusable_elements import next_fab


async def category_page(category: str|None, warehouse: Warehouse, ld:LeftDrawer, rd:RightDrawer) -> None:
    # Create One grid for each unique Category in the first Column
    rd.hide()
    path = f"{warehouse.name}/{category}" if category else warehouse.name
    ui.page_title(path)
    LOGGER.debug(f"Creating Grid for {path}...")
    await create_aggrid(warehouse, category, cart=False)
    next_fab(settings.cart)
    LOGGER.info(f"Created Grid for: {path}")
