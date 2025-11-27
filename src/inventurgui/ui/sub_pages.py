from pathlib import Path
from nicegui import ui

from inventurgui.helper.config import config
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.helper.logger import LOGGER
from inventurgui.ui.grid import create_aggrid


class SubPage:
    help_path: Path
    pages: dict[str, str]
    nc: Nextcloud

    def help(self):
        # Create one Tab for displaying help
        LOGGER.debug(f"Creating Help Panel with the content of {self.help_path}...")
        with ui.row().classes('w-screen p-2 m-0') as row:
            with ui.card().tight().classes(
                    'md:w-1/2 w-full pl-10 pb-20 bg-black m-0 text-base font-light text-secondary decoration-primary'):
                with open(self.help_path, 'r') as f:  # open file
                    ui.markdown(f.read())

    def everything(self):
        # Create one Grid for displaying everything
        LOGGER.debug('Creating the show all grid...')
        grid = create_aggrid(self.nc.data, config) #TODO move helper to Grid class
        #grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeAllColumns'))
        LOGGER.debug(f"Created grid with props: {grid.props}")

    def category(self, category:str):
        # Create One grid for each unique Category in the first Column
        # grids = [ui.aggrid]
        LOGGER.debug(f'Creating Grid for {category}...')
        category_data = self.nc.data[self.nc.data[config['data']['category']] == category]

        grid = create_aggrid(category_data, config)
        LOGGER.debug(f"Created grid with props: {grid.props}")
            # with ui.row():
            #   ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
            #  ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))
