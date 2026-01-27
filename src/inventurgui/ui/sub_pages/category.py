from nicegui import ui
from nicegui.elements.aggrid import AgGrid

from inventurgui.helper.config import config, load_config
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import checkout_fab


def category_page(category: str, warehouse: Warehouse) -> None:
    warehouse_conf: dict = load_config()["warehouse"]
    # Create One grid for each unique Category in the first Column
    ui.page_title(f"{warehouse.name}/{category}")
    LOGGER.debug(f"Creating Grid for {warehouse.name}/{category}...")
    category_data = warehouse.inventory[warehouse.inventory[config["data"]["category"]] == category]
    if category == warehouse_conf.get("everything"):
        category_data = warehouse.inventory
    if category == warehouse_conf.get("selection"):
        category_data = warehouse.selected()
    grid: AgGrid = create_aggrid(warehouse.name, category_data, cart=False)
    checkout_fab(config["cart"])
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")
