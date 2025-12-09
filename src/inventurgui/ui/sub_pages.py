from collections.abc import Callable
from pathlib import Path
from typing import Generator, Iterator, Hashable, Any, Coroutine

from nicegui import ui, app, run
from nicegui.elements.aggrid import AgGrid
from pandas import Series, DataFrame

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import tool_buttons


def get_selected(iterator:Callable[Iterator[tuple[Hashable, Series[Any]]]], row_ids:list[str]) -> DataFrame:
    def _match_selected() -> Generator[Series, None, None]:
        for row_id in row_ids:
            for i, row_data in iterator():
                if str(i) == row_id:
                    yield row_data
    return DataFrame.from_records([r for r in _match_selected()])

def get_df(w:Warehouse) -> Coroutine[Any, Any, DataFrame]:
    LOGGER.debug(f'Task started for {w.name}...')
    row_ids: list = list(app.storage.user.get(w.name))
    return run.cpu_bound(get_selected, w.inventory.iterrows, row_ids)

async def get_results(tasks:list[Coroutine[Any, Any, DataFrame]]):
    results = [await task for task in tasks]
    count = 0
    for result in results:
        df = result
        if not df.empty:
            count += 1
            name = df['warehouse'].unique()[0]
            yield count, name, df

async def truck_page(warehouses:list[Warehouse]) -> None:
    LOGGER.debug(f'Creating Cart page...')
    tasks = [get_df(w) for w in warehouses]

    ui.query(".nicegui-sub-pages").style(replace='gap:0')
    tabs = ui.tabs().classes('bg-dark lg:w-[calc(100vw-250px)] h-[56px] m-0 p-0').props(
            'height=56px flat active-bg-color=secondary active-color=primary mobile-arrows stretch')
    tab_panels = ui.tab_panels(tabs).classes('w-dvw')

    async for count, name, df in get_results(tasks):
        with tabs:
            with ui.tab(str(count)) as tab:
                with ui.row():
                    ui.icon(config['cart']['icon'], size='sm')
                    ui.label(name.upper())
                tab.classes('text-center w-full font-bold subpixel-antialiased tracking-widest')
                tab.props('inline-label')
                badge = ui.badge('0', text_color='dark').props("rounded floating")
                badge.bind_text_from(app.storage.user, name, lambda e: len(e))
        with tab_panels:
            with ui.tab_panel(str(count)).classes('m-0 p-0 w-full'):
                grid: AgGrid = create_aggrid(name, df, config, cart=True)
                tool_buttons(grid)
        tab_panels.set_value(str(1))
        tab.set_label('')
    #if not app.storage.user.get('notified')['truck']:
    ui.notify("Bitte passe die Stückzahlen an indem du darauf klickst.", position='center', timeout=3000, close_button=True, classes='')
    app.storage.user['notified']['truck'] = True
    LOGGER.info(f"Created grid for cart page")

def form_page():
    with ui.tab_panel('test').classes('w-screen h-screen p-0 m-0'):
        with ui.scroll_area().classes('h-[calc(100vh-52px)]'):
            with ui.grid(columns=1).classes('xl:w-1/2 w-full p-3 max-sm:p-0'):
                props = 'color=secondary'
                classes = 'self-start'
                ui.input('Camp/Organisation').classes(classes).props(props)
                ui.input('Ort').classes(classes).props(props)
                ui.date_input('Start Aufbau').classes(classes).props(props)
                ui.date_input('Ende Aufbau').classes(classes).props(props)
                ui.input('E-Mail-Adresse').classes(classes).props(props)
                ui.input('Eingeplante Spende').classes(classes).props(props)
                ui.editor(placeholder='Deine Mail an uns...').classes(f"{classes}").props(props)
                ui.checkbox('Ich habe die Leihbedingungen gelesen.').classes(classes).props(props)
                ui.button('Abschicken')

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
