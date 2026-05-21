import time

from nicegui import app, ui, PageArguments

from dataviewer.helper.config import settings
from dataviewer.helper.i18n import i18n
from dataviewer.helper.logger import LOGGER
from dataviewer.io.cache import Cache
from dataviewer.io.selection import Selection
from dataviewer.ui.grid.grid import create_aggrid
from dataviewer.ui.helper.reusable_elements import badge, next_fab, tabs, tab_panels, back_fab


async def cart_page(warehouses: list[Selection], args: PageArguments) -> None:
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
    for w in warehouses:
        selected = w.selected()
        if selected.is_empty():
            continue
        with truck_tabs:
            with ui.tab(w.name.upper()).props('alert="primary" alert-icon="guitar"'):
                badge("").bind_text_from(app.storage.user["selected"], w.name, backward=lambda v: len(v))
        with truck_panels:
            with ui.tab_panel(w.name.upper()).classes("m-0 p-0 w-full"):
                await create_aggrid(w, cart=True)
        if not truck_panels.value:
            truck_panels.set_value(w.name.upper())
    LOGGER.info("Created cart page")
    next_fab(settings.form)
    back_fab(settings.selection)
