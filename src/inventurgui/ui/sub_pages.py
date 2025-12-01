from pathlib import Path
from typing import Tuple

from nicegui import ui
from pandas.core.interchange.dataframe_protocol import DataFrame

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.io.nextcloud import Warehouse
from inventurgui.ui.grid import create_aggrid

def help_page(help_file:Path = get_path(config['help']['path'])):
    # Create one Page for displaying help
    LOGGER.debug(f"Creating Help Panel with the content of {help_file}...")
    with ui.row().classes('w-screen p-2 m-0') as row:
        with open(help_file, 'r') as f:  # open file
            ui.markdown(f.read()).classes('pl-10 pb-20 m-0 text-base font-light text-secondary')

def warehouse_page(warehouse: Warehouse):
    # Create one Grid for displaying everything inside a warehouse
    LOGGER.debug(f'Creating the show all grid for {warehouse['name']}...')
    grid = create_aggrid(warehouse['inventory'], config)  # TODO move helper to Grid class
    # grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeAllColumns'))
    LOGGER.debug(f"Created grid with props: {grid.props}")

def category_page(warehouse: Warehouse):
    # Create One grid for each unique Category in the first Column
    # grids = [ui.aggrid]
    inventory = warehouse['inventory']
    categories = sorted(inventory[config['data']['category']].unique())
    for category in categories:
        LOGGER.debug(f'Creating Grid for {category}...')
        category_data = inventory[inventory[config['data']['category']] == category]
        grid = create_aggrid(category_data, config)
        LOGGER.debug(f"Created grid with props: {grid.props}")
        # with ui.row():
        #   ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
        #  ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))
