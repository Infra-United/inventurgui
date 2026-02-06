from nicegui import ui

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import checkout_fab


def category_page(category: str, warehouse: Warehouse) -> None:
    # Create One grid for each unique Category in the first Column
    ui.page_title(f"{warehouse.name}/{category}")
    LOGGER.debug(f"Creating Grid for {warehouse.name}/{category}...")
    category_data = warehouse.inventory[warehouse.inventory[settings.columns["category"]] == category]
    if category == settings.warehouse.get("everything"):
        category_data = warehouse.inventory
    if category == settings.warehouse.get("selection"):
        category_data = warehouse.selected()
    if category == settings.admin['edits'] and authenticate_user():
        category_data = warehouse.selected()
    create_aggrid(warehouse.name, category_data, cart=False)
    checkout_fab(settings.cart)
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")
