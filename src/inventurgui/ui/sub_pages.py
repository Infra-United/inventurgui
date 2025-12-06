from pathlib import Path

import pandas as pd
from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from pandas.core.interchange.dataframe_protocol import DataFrame

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import tool_buttons


def cart_page(warehouses:list[Warehouse]) -> None:
    LOGGER.debug(f'Creating Grid for cart page...')
    selected = pd.concat(w.selected for w in warehouses)
    print(selected)
    with ui.tabs().classes('w-screen h-[56px] m-0 p-0').props('height=56px flat') as tabs:
        selection_tab = ui.tab(str(config['cart']['grid']).upper(), icon='edit_note')
        selection_tab.classes('text-center bg-secondary font-bold subpixel-antialiased tracking-widest')
        form_tab = ui.tab(name=str(config['cart']['form']).upper())
        form_tab.classes('m-0 p-0 text-center font-bold subpixel-antialiased tracking-widest')
    with ui.tab_panels(tabs, value=selection_tab):
        with ui.tab_panel(selection_tab).classes('m-0 p-0') as selection_tab_panel:
            grid: AgGrid = create_aggrid('cart', selected, config)
        with ui.tab_panel(form_tab).classes('w-screen h-screen') as form_tab_panel:
            with ui.grid(columns=1).classes('xl:w-1/2 w-full m-0'):
                props = 'color=secondary'
                classes = 'self-start'
                ui.input('Camp/Organisation').classes(classes).props(props)
                ui.input('Ort').classes(classes).props(props)
                ui.date_input('Start Aufbau').classes(classes).props(props)
                ui.date_input('Ende Aufbau').classes(classes).props(props)
                ui.input('E-Mail-Adresse').classes(classes).props(props)
                ui.input('Eingeplante Spende').classes(classes).props(props)
                ui.textarea('Anmerkungen').classes(f"{classes}").props(props)
    #for w in warehouses:
     #   if not w.selected.empty:
      #      with ui.expansion(w.name, group='cart'):
    #ui.notify("Hier ist deine Auswahl. Bitte passe die Stückzahlen an, in dem du darauf klickst.", position='top', type='ongoing', close_button=True)
    #tool_buttons(grid)
    LOGGER.info(f"Created grid for cart page")

def help_page(help_file:Path = get_path(config['help']['path'])) -> None:
    # Create one Page for displaying help
    LOGGER.debug(f"Creating Help Panel with the content of {help_file}...")
    with ui.row().classes('w-screen p-2 m-0'):
        with open(help_file, 'r') as f:  # open file
            ui.markdown(f.read()).classes('pl-10 pb-20 m-0 text-base font-light text-secondary')

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
