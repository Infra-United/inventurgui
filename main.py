from logging import debug
import random
import string
from nicegui import app, ui
from ui.admin import admin
from ui.auth import login
from config.data import data
from config.config import config, theme
from ui.grid import create_aggrid, handle_links

@ui.page('/')
def main(): 
    # Set colors and clear browser storage
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    # app.storage.clear()    
    
    # Create Tabs
    debug('Creating Tabs...')
    with ui.header().classes('fixed p-0 m-0 bg-secondary text-primary') as header:
        with ui.tabs().classes('w-full') as tabs:
            # Create one Tab for showing Help
            if config['help']['display']:
                help = ui.tab(name='help', label=config['help']['label'], icon='help').classes('')
            # Create one Tab for showing everything
            if config['everything']['display']:
                everything = ui.tab(name='everything', label=config['everything']['label'])
            # Create one Tab for each category
            categories:list[str] = sorted(data[config['data']['category']].unique())
            for category in categories:
                ui.tab(category).classes('')
    
    # check for links and convert them to icon if enabled
    if config['links']['display']:
        handle_links(data, config['links']['name'])                                                     
    
    # Create Tab Panels (what is shown when Tab is selected)
    debug('Creating Tab Panels (Content)...')
    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=help).classes('w-full h-full fixed'):
            # Create one Tab for displaying help
            debug(f"Creating Help Panel with the content of {config['help']['path']}...")
            with ui.tab_panel(help):                
                with open(config['help']['path'], 'r') as f: # open file 
                    with ui.card().classes('md:w-1/2 w-full h-dvh pl-10 pb-20 bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                        ui.markdown(f.read()).classes('') 
            
            # Create one Grid for displaying everything
            debug('Creating the show all grid...')
            with ui.tab_panel(everything):
                grid = create_aggrid(data, config)
        
            # Create One grid for each unique Category in the first Column
            # grids = [ui.aggrid] 
            debug('Creating one Grid for each Category...')
            for category in categories:
                category_data = data[data[config['data']['category']]==category]
                with ui.tab_panel(category):
                    grid = create_aggrid(category_data, config)
                    with ui.row():
                        ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
                        ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))

    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    debug('Finished. Starting UI...')
    storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
    ui.run(title=config['title'], favicon=config['favicon'], port=8081, storage_secret=storage_secret)
    debug('Successfully started UI.')
    
if __name__ in {"__main__", "__mp_main__"}:                        
    main()
    
