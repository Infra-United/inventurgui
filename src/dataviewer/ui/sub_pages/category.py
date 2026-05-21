from nicegui import ui

from dataviewer.helper.config import settings
from dataviewer.helper.logger import LOGGER
from dataviewer.io.selection import Selection
from dataviewer.ui.grid.grid import create_aggrid
from dataviewer.ui.helper.reusable_elements import next_fab


async def category_page(category: str | None, selection: Selection) -> None:
    path = f"{selection.name}/{category}" if category else selection.name
    ui.page_title(path)
    LOGGER.debug(f"Creating Grid for {path}...")
    await create_aggrid(selection, category, cart=False)
    next_fab(settings.cart)
    # save_fab(warehouse)
    LOGGER.info(f"Created Grid for: {path}")
