"""from nicegui import ui
from nicegui.elements.drawer import RightDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.ui.grid.grid import create_aggrid


async def request_page(name: str, rd: RightDrawer|None) -> None:
    rd.hide() if rd else None
    path = f"{settings.requests['label']}/{name}" if name else settings.requests['label']
    ui.page_title(path)
    LOGGER.debug(f"Creating Grid for {path}...")
    await create_aggrid(name, cart=True)
    if authenticate_user():
        save_fab(warehouse)
    else:
        next_fab(settings.cart)
    LOGGER.info(f"Created Grid for: {path}")
"""