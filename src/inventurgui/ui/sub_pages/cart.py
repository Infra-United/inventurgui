import time

from nicegui import app, ui, PageArguments
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import load_config
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import checkout_fab, tabs, tab_panels
from inventurgui.helper.magic_link import load_data_from_magic_link


def cart_page(ld: LeftDrawer, warehouses: list[Warehouse], args: PageArguments) -> None:
    cart: dict = load_config()["cart"]
    ui.query(".nicegui-sub-pages").classes(replace="bg-dark w-full no-scroll").style(replace="gap:0")

    current_id = app.storage.browser["id"]
    request_id = args.query_parameters.get("id")
    if current_id != request_id:
        load_data_from_magic_link(current_id, request_id)

    if Cache.total() == 0:
        ui.notify(cart["select_tip"], type="warning", position="center", color="primary", textColor="dark")
        time.sleep(1)
        ui.navigate.to(f"/{url_safe(load_config()['warehouse'].get('label'))}")
        return
    if not Cache.notified() and Cache.total() != 0:
        ui.notify(cart["edit_tip"], position="center", color="primary", textColor="dark")
        app.storage.user.update({"notified": True})

    ui.page_title(f"{cart['label']}")
    ld.hide()
    truck_tabs = tabs()
    truck_panels = tab_panels(truck_tabs)
    LOGGER.debug("Creating Cart page...")
    for w in warehouses:
        selected = w.selected()
        if selected is None or selected.empty:
            continue
        with truck_tabs:
            with ui.tab(w.name.upper(), icon=cart["tab_icon"]):
                badge = ui.badge("0", color="white", text_color='secondary').props("").classes("text-bold ml-2 p-1")
                badge.bind_text_from(app.storage.user, w.name, lambda e: len(e))
        with truck_panels:
            with ui.tab_panel(w.name.upper()).classes("m-0 p-0 w-full"):
                create_aggrid(w.name, selected, cart=True)
    truck_panels.set_value(warehouses[0].name.upper())
    LOGGER.info("Created cart page")
    checkout_fab(load_config()["form"])
