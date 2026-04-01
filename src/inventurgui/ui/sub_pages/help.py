from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.ui.helper.markdown import render_markdown
from inventurgui.ui.helper.reusable_elements import share_fab


async def help_page(ld: LeftDrawer, md: dict[str, str]):
    ld.hide()
    ui.page_title(f"{settings.help['label']}")
    LOGGER.debug(f"Creating help page...")
    with ui.tab_panel("help").classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        render_markdown(md.get(settings.help["label"]))

async def wiki_page(name: str, content: str, ld: LeftDrawer, style: str):
    ld.hide()
    ui.page_title(f"{name.capitalize()}")
    LOGGER.debug(f"Creating wiki page {name}...")

    with ui.tab_panel(name).classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        if settings.help["wiki"]:
            html = ui.html(f"<head>{style}</head> {content}", sanitize=False)
            html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
            html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
            share_fab(name, content)