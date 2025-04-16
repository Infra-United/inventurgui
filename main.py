import logging
from logging import debug
import random
import string
from nicegui import app, ui
from config.users import hash_password
#from ui.admin import admin
#from ui.auth import try_login
from config.data import data
from config.config import config, theme
from ui.grid import create_aggrid

@ui.page('/')
def main():
    # Set colors and clear browser storage
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    # app.storage.clear()    
    
    # Create Tabs
    debug('Creating Tabs...')
    with ui.header().classes('p-0 m-0 h-50px bg-secondary text-primary') as header:
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
    # Create Tab Panels (what is shown when Tab is selected)
    debug('Creating Tab Panels (Content)...')

    with ui.card().tight().classes('w-screen bg-black container overflow-auto p-0'):
        with ui.tab_panels(tabs, value=help).classes('w-full h-dvh fixed'):
            # Create one Tab for displaying help
            debug(f"Creating Help Panel with the content of {config['help']['path']}...")
            with ui.tab_panel(help).classes('p-0 m-0'):
                with ui.row().classes('w-screen p-0 m-0'):
                    with ui.card().tight().classes('md:w-1/2 w-full pl-10 pb-20 m-0 bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                        with open(config['help']['path'], 'r') as f: # open file 
                            ui.markdown(f.read())
                  #  with ui.card().classes('m-0 h-dvh content-center bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                  #      with ui.card().classes(''):
                #            username = ui.input('Username').value
                 #           password = ui.input('Password', password=True, password_toggle_button=True).value
                          #  ui.button('Log in/Register', on_click=try_login(username, hash_password(password)))
            
            # Create one Grid for displaying everything
            debug('Creating the show all grid...')
            with ui.tab_panel(everything).classes('p-0 m-0'):
                grid = create_aggrid(data, config)
                grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeAllColumns'))
        
            # Create One grid for each unique Category in the first Column
            # grids = [ui.aggrid] 
            debug('Creating one Grid for each Category...')
            for category in categories:
                category_data = data[data[config['data']['category']]==category]
                with ui.tab_panel(category).classes('p-0 m-0'):
                    grid = create_aggrid(category_data, config)
                    #with ui.row():
                     #   ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
                      #  ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))

    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    debug('Finished. Starting UI...')
    storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
    ui.run(title=config['title'], favicon=config['favicon'], port=8080, storage_secret=storage_secret)
    debug('Successfully started UI.')
    
if __name__ in {"__main__", "__mp_main__"}:                        
    main()
    
