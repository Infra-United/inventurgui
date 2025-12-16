from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import config, request_conf
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import checkout_fab, tabs, tab_panels


async def cart_page(ld:LeftDrawer, warehouses:list[Warehouse]) -> None:
    total = app.storage.user.get('Total', 0)
    if total == 0:
        ui.notify(config['cart']['select_tip'], position='center', color='primary', textColor='dark')
        ui.navigate.to('/')
        return
    if not app.storage.user.get('notified')['selection'] and total != 0:
        ui.notify(config['cart']['edit_tip'], position='center', color='primary', textColor='dark')
        app.storage.user['notified']['selection'] = True
    ld.hide()
    truck_tabs = tabs()
    truck_panels = tab_panels(truck_tabs)
    LOGGER.debug(f'Creating Cart page...')
    for w in warehouses:
        selected = await w.selected()
        if selected is None or selected.empty:
            continue
        with truck_tabs:
            with ui.tab(w.name.upper(), icon=config['cart']['icon']).classes('px-7').props('inline-label'):
                badge = ui.badge('0', color='accent').props("floating").classes('text-bold')
                badge.bind_text_from(app.storage.user, w.name, lambda e: len(e))
        with truck_panels:
            with ui.tab_panel(w.name.upper()).classes('m-0 p-0 w-full'):
                grid: AgGrid = create_aggrid(w.name, selected, config, cart=True)
    truck_panels.set_value(warehouses[0].name.upper())
    LOGGER.info(f"Created cart page")
    checkout_fab(request_conf)
