from contextlib import suppress

from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.ui.helper.markdown import render_markdown


def start_page(ld: LeftDrawer, md: dict[str,str]) -> None:
    LOGGER.debug("Creating start page...")
    ui.page_title(settings.title)
    with ui.tab_panel(settings.start['label']).classes("m-0 p-0 w-full scroll h-dvh"):
        render_markdown(md.get(settings.start['label']))
    with suppress(TypeError):
        ui.on('resize', lambda e: ld.show() if e.args['width'] >= 1024 else ld.hide(), trailing_events=True)
