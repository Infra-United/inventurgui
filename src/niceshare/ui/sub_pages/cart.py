import time

from nicegui import app, ui

from niceshare.helper.config import settings
from niceshare.helper.i18n import i18n
from niceshare.helper.logger import LOGGER
from niceshare.io.cache import Cache
from niceshare.io.selection import Selection
from niceshare.ui.grid.grid import create_aggrid
from niceshare.ui.helper.reusable_elements import badge, next_fab, tabs, tab_panels, back_fab


async def cart_page(warehouses: list[Selection]) -> None:
    ui.query(".nicegui-sub-pages").classes(replace="bg-dark w-full no-scroll").style(replace="gap:0")

    if Cache.total() == 0:
        ui.notify(i18n.get("cart.select_tip"), type="warning", position="center", color="primary", textColor="dark")
        time.sleep(1)
        ui.navigate.to("/")
        return
    if not Cache.notified() and Cache.total() != 0:
        ui.notify(i18n.get("cart.edit_tip"), position="center", color="primary", textColor="dark")
        app.storage.user.update({"notified": True})

    ui.page_title(f"{settings.cart['label']}")
    truck_tabs = tabs()
    truck_panels = tab_panels(truck_tabs)
    LOGGER.debug("Creating Cart page...")
    w = warehouses[0]
    with truck_tabs:
        with ui.tab(w.name.upper()).props(f'alert="primary" alert-icon="{settings.cart['tab_icon']}"'):
            badge("").bind_text_from(
                app.storage.user,
                "selected",
                backward=lambda v: len(v)
            )
    with truck_panels:
        with ui.tab_panel(w.name.upper()).classes("m-0 p-0 w-full"):
            await create_aggrid(w.name, w.selected(), cart=True)
    if not truck_panels.value:
        truck_panels.set_value(w.name.upper())
    LOGGER.info("Created cart page")
    next_fab(settings.form)
    back_fab(settings.selection)
