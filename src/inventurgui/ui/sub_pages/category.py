from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.grid.grid import create_aggrid
from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.reusable_elements import checkout_fab


def category_page(category: str, warehouse: Warehouse, ld:LeftDrawer) -> None:
    # Create One grid for each unique Category in the first Column
    ld.show()
    ui.page_title(f"{warehouse.name}/{category}")
    LOGGER.debug(f"Creating Grid for {warehouse.name}/{category}...")
    create_aggrid(warehouse, category, cart=False)
    checkout_fab(settings.cart)
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")
