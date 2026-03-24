from nicegui import ui
from nicegui.elements.drawer import RightDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.ui.helper.markdown import render_markdown


def start_page(rd: RightDrawer | None, md: dict[str, str]) -> None:
    rd.hide() if rd else None
    LOGGER.debug("Creating start page...")
    ui.page_title(settings.title)
    with ui.tab_panel(settings.start["label"]).classes("m-0 p-0 max-sm:pb-20 w-full scroll h-dvh"):
        render_markdown(md.get(settings.start["label"]))
