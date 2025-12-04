from pathlib import Path

from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid, grid_buttons


def help_page(help_file:Path = get_path(config['help']['path'])):
    # Create one Page for displaying help
    LOGGER.debug(f"Creating Help Panel with the content of {help_file}...")
    with ui.row().classes('w-screen p-2 m-0') as row:
        with open(help_file, 'r') as f:  # open file
            ui.markdown(f.read()).classes('pl-10 pb-20 m-0 text-base font-light text-secondary')
def warehouse_page(warehouse: Warehouse, ld:LeftDrawer):
    # Create one Grid for displaying everything inside a warehouse
    LOGGER.debug(f'Creating the show all grid for {warehouse.name}...')
    grid:AgGrid = create_aggrid(warehouse.name, warehouse.inventory, config)
    for row in app.storage.user[warehouse.name]:
        grid.run_row_method(row, 'setSelected', True)
    grid_buttons(grid)
    #grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeAllColumns'))
    LOGGER.debug(f"Created grid with props: {grid.props}")

def category_page(category:str, warehouse: Warehouse):
    # Create One grid for each unique Category in the first Column
    LOGGER.debug(f'Creating Grid for {category}...')
    category_data = warehouse.inventory[warehouse.inventory[config['data']['category']] == category]
    grid:AgGrid = create_aggrid(warehouse.name, category_data, config)

    for row in app.storage.user[warehouse.name]:
        grid.run_row_method(row, 'setSelected', True)
    grid_buttons(grid)
    LOGGER.debug(f"Created grid with props: {grid.props}")
    # with ui.row():
    #   ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
    #  ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))
