from nicegui import ui
from nicegui.elements.drawer import RightDrawer, LeftDrawer

from inventurgui.helper.logger import LOGGER


async def wiki_page(name: str, html: str, ld: LeftDrawer, rd: RightDrawer, style: str):
    ld.hide()
    ui.page_title(name)
    LOGGER.debug(f"Creating wiki page {name}...")
    with ui.tab_panel(name).classes("m-0 p-0 items-center w-full scroll h-dvh"):
        html = ui.html(f"<head>{style}</head> {html}", sanitize=False)
        html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
        html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
