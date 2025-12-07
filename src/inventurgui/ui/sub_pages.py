import asyncio
from asyncio import gather
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Generator, AsyncGenerator, Iterator, Hashable, Any, Coroutine

import pandas as pd
from nicegui import ui, app, run
from nicegui.elements.aggrid import AgGrid
from pandas import Series, DataFrame

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import tool_buttons

def get_selected(iterator:Callable[Iterator[tuple[Hashable, Series[Any]]]], row_ids:list[str]):
    def _match_selected() -> Generator[Series, None, None]:
        for row_id in row_ids:
            for i, row_data in iterator():
                if str(i) == row_id:
                    yield row_data
    return DataFrame.from_records([r for r in _match_selected()])

async def get_df(w:Warehouse) -> Coroutine[Any, Any, DataFrame]:
    LOGGER.debug(f'Task started for {w.name}...')
    row_ids: list = list(app.storage.user.get(w.name))
    return run.cpu_bound(get_selected, w.inventory.iterrows, row_ids)

async def cart_page(warehouses:list[Warehouse]) -> None:
    LOGGER.debug(f'Creating Cart page...')
    tasks = [get_df(w) for w in warehouses]
    ui.query(".nicegui-sub-pages").style(replace='gap:0')
    with ui.tabs().classes('bg-dark w-screen h-[56px] m-0 p-0').props('dense height=56px flat active-bg-color=secondary active-color=primary') as tabs:
        form_tab = ui.tab(name=str(config['cart']['form']).upper())
        form_tab.classes('m-0 p-0 w-1/2 text-center font-bold subpixel-antialiased tracking-widest')
        selection_tab = ui.tab(str(config['cart']['grid']).upper())
        selection_tab.classes('text-center w-1/2 font-bold subpixel-antialiased tracking-widest')
    with ui.tab_panels(tabs, value=form_tab):
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
        with ui.tab_panel(selection_tab).classes('m-0 p-0') as selection_tab_panel:
            results = [await task for task in tasks]
            selected = pd.concat([await result for result in results])
            LOGGER.debug("Got Results from Tasks.")
            grid: AgGrid = create_aggrid('cart', selected, config)

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
