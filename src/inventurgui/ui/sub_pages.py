import datetime
import re

import requests
from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.tabs import Tabs

from inventurgui.helper.config import config, get_path, EMAIL_REGEX, start
from inventurgui.helper.logger import LOGGER
from inventurgui.io.mail import Mail
from inventurgui.io.request import Request
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import tool_buttons

def tabs():
    return ui.tabs().classes('bg-secondary h-[56px] w-full scroll m-0 p-0').props(
        'height=56px active-bg-color=accent inline-label mobile-arrows stretch')

def tab_panels(tabs:Tabs):
    return ui.tab_panels(tabs).classes('w-full h-dvh')

async def truck_page(warehouses:list[Warehouse]) -> None:
    truck_tabs = tabs()
    truck_panels = tab_panels(truck_tabs)
    LOGGER.debug(f'Creating Cart page...')
    for w in warehouses:
        selected = await w.selected
        if selected is None or selected.empty:
            continue
        with truck_tabs:
            with ui.tab(w.name.upper(), icon=config['menu']['truck']['icon']) as tab:
                tab.classes('text-center w-full font-bold subpixel-antialiased tracking-widest')
                tab.props('inline-label')
                badge = ui.badge('0', color='accent').props("floating").classes('text-bold')
                badge.bind_text_from(app.storage.user, w.name, lambda e: len(e))
        with truck_panels:
            with ui.tab_panel(w.name.upper()).classes('m-0 p-0 w-full'):
                grid: AgGrid = create_aggrid(w.name, selected, config, cart=True)
    truck_panels.set_value(warehouses[0].name.upper())
    total = app.storage.user.get('Total')
    if not app.storage.user.get('notified')['selection'] and total != 0:
        ui.notify(config['selection']['edit_tip'], position='center', color='primary', textColor='dark')
        app.storage.user['notified']['selection'] = True
    elif total == 0:
        ui.notify(config['selection']['select_tip'], position='center', color='primary', textColor='dark')
    LOGGER.info(f"Created grid for cart page")

def form_page():
    request = Request()
    today = datetime.date.today()
    with ui.grid(columns=1).classes('xl:w-1/2 w-full p-5 bg-dark h-screen'):
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


def main_page() -> None:
    # Create one Page for displaying help
    main_tabs = tabs()
    main_panels = tab_panels(main_tabs)
    for key, values in start.items():
        if not values['display']:
            continue
        with main_tabs:
            label = values['label']
            with ui.tab(label, icon=values['icon']) as tab:
                tab.classes('text-center w-full font-bold subpixel-antialiased tracking-widest')
                tab.props('inline-label')
        with main_panels:
            with ui.tab_panel(label).classes('m-0 p-0'):
                path = get_path(values.get('path'))
                try:
                    with open(path, 'r') as f:  # open file
                        LOGGER.debug(f"Creating {label} with the content of {path}...")
                        text = f.read()
                except FileNotFoundError:
                    if url:=values.get('url'):
                        LOGGER.debug(f"Getting {label} content from {url}...")
                        text = requests.get(url).text
                        with open(path, 'w') as f: f.write(text)
                        LOGGER.info(f"Successfully fetched {label} content from {url}!")
                    else:
                        text = (f"<br><code>{key}:<br>  path:{path.name} </code><br> in config does not exist."
                                 f"<br>Please review your config, read the logs and check /files."
                                 f"<br>If you started the program for the first time i may have fetched the page by now."
                                 f"<br>In that case a page reload might also fix the problem.")
                ui.markdown(text).classes('p-10 pt-5 m-0 text-pretty text-base/8 text-gray-300')
    main_panels.set_value([tab.props.get('label') for tab in main_tabs.descendants()][0]) # First tab is open by default

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
