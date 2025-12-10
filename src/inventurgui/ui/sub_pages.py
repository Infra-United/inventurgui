import datetime
import re
from collections.abc import Callable
from pathlib import Path
from typing import Generator, Iterator, Hashable, Any, Coroutine

from nicegui import ui, app, run
from nicegui.elements.aggrid import AgGrid
from pandas import Series, DataFrame

from inventurgui.helper.config import config, get_path, EMAIL_REGEX
from inventurgui.helper.logger import LOGGER
from inventurgui.io.mail import Mail
from inventurgui.io.request import Request
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import tool_buttons

async def truck_page(warehouses:list[Warehouse]) -> None:

    ui.query(".nicegui-sub-pages").style(replace='gap:0')
    with ui.row().classes('w-screen gap-0'):
        tabs = ui.tabs().classes('bg-dark h-[56px] w-full scroll m-0 p-0').props(
                'height=56px active-bg-color=secondary inline-label mobile-arrows active-color=primary stretch')
        tab_panels = ui.tab_panels(tabs).classes('w-dvw')

    LOGGER.debug(f'Creating Cart page...')
    for w in warehouses:
        selected = await w.selected
        if selected.empty:
            continue
        with tabs:
            with ui.tab(w.name.upper(), icon=config['truck']['icon']) as tab:
                tab.classes('text-center w-full font-bold subpixel-antialiased tracking-widest')
                tab.props('inline-label')
                badge = ui.badge('0', text_color='dark').props("rounded floating")
                badge.bind_text_from(app.storage.user, w.name, lambda e: len(e))
        with tab_panels:
            with ui.tab_panel(w.name.upper()).classes('m-0 p-0 w-full'):
                grid: AgGrid = create_aggrid(w.name, selected, config, cart=True)
    tab_panels.set_value(warehouses[0].name.upper())
    if not app.storage.user.get('notified')['truck']:
        ui.notify(config['truck']['tip'], position='center', color='primary', textColor='dark')
    app.storage.user['notified']['truck'] = True
    LOGGER.info(f"Created grid for cart page")

def form_page():
    with ui.card().classes('w-screen h-screen p-0 m-0'):
        with ui.scroll_area().classes('h-[calc(100vh-52px)]'):
            request = Request()
            today = datetime.date.today()
            with ui.grid(columns=1).classes('xl:w-1/2 w-full p-3 max-sm:p-0'):
                name = ui.input(config['form']['name']).bind_value(request, 'name')
                place = ui.input(config['form']['place']).bind_value(request, 'place')
                start = ui.date_input(config['form']['start'], placeholder='DD.MM.YYYY').bind_value(request, 'start')
                start.picker.props[':options'] = f'date => date >= "{today:%Y/%m/%d}"'
                start.picker.props['mask'] = 'DD.MM.YYYY'
                end = ui.date_input(config['form']['end'], placeholder='DD.MM.YYYY').bind_value(request, 'end')
                end.picker.props[':options'] = f'date => date >= "{today:%Y/%m/%d}"'
                end.picker.props['mask'] = 'DD.MM.YYYY'
                email = ui.input(config['form']['email'], validation={'Not a valid email': lambda v: True if re.match(EMAIL_REGEX, v) else False})
                email.bind_value(request, 'email')
                email.on_value_change(lambda c: submit.enable() if c.value and email.validate() else submit.disable())
                donation = ui.input(config['form']['donation']).bind_value(request, 'donation')
                message = ui.editor(placeholder='Deine Mail an uns...').bind_value(request, 'message')
                check = ui.checkbox(config['form']['checkbox']).bind_value(request, 'checkbox')
                check.on_value_change(lambda c: submit.enable() if c.value and email.validate() else submit.disable())
                submit = ui.button(config['form']['submit'])
                submit.disable()
                submit.on_click(lambda: Mail.send_mail(request.html, request.text, request.subject, request.email))


def help_page(help_file:Path = get_path(config['help']['path'])) -> None:
    # Create one Page for displaying help
    LOGGER.debug(f"Creating Help Panel with the content of {help_file}...")
    with ui.row().classes('w-screen p-2 m-0'):
        with open(help_file, 'r') as f:  # open file
            ui.markdown(f.read()).classes('pl-10 pb-20 m-0 text-base font-light text-primary')

def category_page(category:str, warehouse: Warehouse) -> None:
    # Create One grid for each unique Category in the first Column
    LOGGER.debug(f'Creating Grid for {warehouse.name}/{category}...')
    category_data = warehouse.inventory[warehouse.inventory[config['data']['category']] == category]
    if category == config['everything']:
        category_data = warehouse.inventory
    grid:AgGrid = create_aggrid(warehouse.name, category_data, config)
    tool_buttons(grid)
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")
    # with ui.row():
    #   ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
    #  ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))
