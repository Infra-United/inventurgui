import time

from nicegui import app, ui, PageArguments

from niceshare.helper.config import settings
from niceshare.helper.i18n import i18n
from niceshare.helper.logger import LOGGER
from niceshare.io.cache import Cache
from niceshare.io.warehouse import Warehouse
from niceshare.ui.grid.grid import create_aggrid
from niceshare.ui.helper.calculations import total_weight
from niceshare.ui.helper.magic_links import load_data_from_magic_link
from niceshare.ui.helper.reusable_elements import badge, next_fab, tabs, tab_panels, back_fab


async def cart_page(warehouses: list[Warehouse], args: PageArguments) -> None:
    ui.query(".nicegui-sub-pages").classes(replace="bg-dark w-full no-scroll").style(replace="gap:0")

    current_id = app.storage.browser["id"]
    request_id = args.query_parameters.get("id")
    if current_id != request_id:
        load_data_from_magic_link(request_id)

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
            with ui.tab(w.name.upper()).props('alert="primary" alert-icon="local_shipping"'):
                Cache.set_weight(w.name, await total_weight(w.name, w.selected()))
                badge("").bind_text_from(
                    app.storage.user["weight"],
                    w.name,
                    backward=lambda v: f"{float(v) / 1000:.2f} t" if v > 1000 else f"{v} kg",
                )
        with truck_panels:
            with ui.tab_panel(w.name.upper()).classes("m-0 p-0 w-full"):
                await create_aggrid(w.name, selected, cart=True)
        if not truck_panels.value:
            truck_panels.set_value(w.name.upper())
    LOGGER.info("Created cart page")
    next_fab(settings.form)
    back_fab(settings.warehouse)
