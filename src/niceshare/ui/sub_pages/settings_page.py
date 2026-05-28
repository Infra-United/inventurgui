from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from niceshare.helper.config import settings
from niceshare.helper.i18n import i18n
from niceshare.helper.logger import LOGGER
from niceshare.io.exporter import export_inventory
from niceshare.io.selection import Selection


def settings_page(ld: LeftDrawer, warehouses:list[Selection]):
    ui.page_title(f"{settings.settings['label']}")
    LOGGER.debug(f"Creating settings page...")
    with ui.tab_panel("settings").classes("m-0 p-10 max-sm:pb-20 items-center w-full scroll h-dvh"):
        ui.label("Achtung: Alle Bilder, Links & Kommentare die hier hochgeladen wurden gehen verloren! Falls du etwas geändert hast, exportiere zunächst.")
        ui.button(i18n.get("settings.reload_dav"), icon='update',
                  on_click=lambda: load_data_from_dav(reload=True)
                ).props("text-color=secondary")
        ui.label("Achtung: Die Inventur in der Cloud wird überschrieben - wenn in der Zwischenzeit was geändert wurde, geht das verloren!")
        ui.button(i18n.get("settings.export_inventory"), icon='update',
                  on_click=lambda: export_inventory(warehouses)
                ).props("text-color=secondary")
