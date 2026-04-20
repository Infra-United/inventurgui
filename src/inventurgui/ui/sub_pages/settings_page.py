from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.logger import LOGGER
from inventurgui.io.exporter import export_inventory
from inventurgui.io.load_data import load_data_from_dav, load_wiki
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user


def settings_page(ld: LeftDrawer, warehouses:list[Warehouse]):
    if not authenticate_user():
        ui.notify(i18n.get("admin.not_admin"), color="negative", position="top")
        ui.navigate.to("/login")
    ld.hide()
    ui.page_title(f"{settings.settings['label']}")
    LOGGER.debug(f"Creating settings page...")
    with ui.tab_panel("settings").classes("m-0 p-10 max-sm:pb-20 items-center w-full scroll h-dvh"):
        ui.label("Achtung: Alle Bilder, Links & Kommentare die hier hochgeladen wurden gehen verloren! Falls du etwas geändert hast, exportiere zunächst.")
        ui.button(i18n.get("settings.reload_dav"), icon='update',
                  on_click=lambda: load_data_from_dav(reload=True)
                ).classes("text-secondary")
        ui.label("Achtung: Die Inventur in der Cloud wird überschrieben - wenn in der Zwischenzeit was geändert wurde, geht das verloren!")
        ui.button(i18n.get("settings.export_inventory"), icon='update',
                  on_click=lambda: export_inventory(warehouses)
                ).classes("text-secondary")
        if settings.help["wiki"]:
            ui.label("Hinweis: Wiki laden dauert ne halbe Minute, läuft im Hintergrund.")
            ui.button(i18n.get("settings.reload_wiki"), icon='update',
                  on_click=lambda: load_wiki(reload=True)
                ).classes("text-secondary")
