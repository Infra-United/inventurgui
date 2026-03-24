
from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.wiki import WIKI_ROOT
from inventurgui.ui.helper.markdown import render_markdown


async def wiki_page(name: str, html: str, ld: LeftDrawer, md: str, style: str):
    ld.hide()
    ui.page_title(f"{WIKI_ROOT.capitalize()}/{name}")
    LOGGER.debug(f"Creating wiki page {name}...")
    with ui.tab_panel(name).classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        if settings.help["wiki"]:
            html = ui.html(f"<head>{style}</head> {html}", sanitize=False)
            html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
            html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
        else:
            render_markdown(md)
