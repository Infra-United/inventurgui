from nicegui import ui

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.grid.grid import create_aggrid
from inventurgui.ui.layout import checkout_fab


def category_page(category: str, warehouse: Warehouse) -> None:
    # Create One grid for each unique Category in the first Column
    ui.page_title(f"{warehouse.name}/{category}")
    LOGGER.debug(f"Creating Grid for {warehouse.name}/{category}...")
    create_aggrid(warehouse, category, cart=False)
    checkout_fab(settings.cart)
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")
