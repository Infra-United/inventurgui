from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.ui.helper.markdown import render_markdown


async def help_page(ld: LeftDrawer, md: dict[str, str]):
    ld.hide()
    ui.page_title(f"{settings.help['label']}")
    LOGGER.debug(f"Creating help page...")
    with ui.tab_panel("help").classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        render_markdown(md.get(settings.help["label"]))