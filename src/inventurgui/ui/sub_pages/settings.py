from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.logger import LOGGER
from inventurgui.io.load_data import load_data


def settings_page(ld: LeftDrawer):
    ld.hide()
    ui.page_title(f"{settings.settings['label']}")
    LOGGER.debug(f"Creating settings page...")
    with ui.tab_panel("settings").classes("m-0 p-10 max-sm:pb-20 items-center w-full scroll h-dvh"):
        ui.button(i18n.get("settings.reload_data"), icon='update',
                  on_click=lambda: load_data(reload=True)
                )
