from nicegui import ui

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.ui.helper.markdown import render_markdown


def start_page(md: dict[str, str]) -> None:
    LOGGER.debug("Creating start page...")
    ui.page_title(settings.title)
    with ui.tab_panel(settings.start["label"]).classes("m-0 p-0 max-sm:pb-20 w-full scroll h-dvh"):
        render_markdown(md.get(settings.start["label"]))
