import logging
from nicegui import ui
from pandas_ods_reader import read_ods
import yaml
from functions.cli import get_args
from functions.grid import check_links, create_grid

@ui.page('/')
def main():
     # get Arguments from Command-Line and set log-level
    args:dict = get_args()
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.debug(f"Args: {args}")
    
    # get Config from yml file
    logging.debug('Loading config file...')
    try:
        with open(args.config_file, 'r') as f: 
            config:dict = yaml.load(f, Loader=yaml.FullLoader) 
    except FileNotFoundError:
        logging.exception('Config File not Found:', args.config_file); exit()
    
    # read ods file to get inventory data
    path = config['data']['path']    
    logging.debug(f"Reading Data from {config['data']['path']}...")
    data = read_ods(path)
    
    # Set colors
    ui.colors(primary=config['colors']['primary'], secondary=config['colors']['secondary'])
        
    # Create Tabs
    logging.debug('Creating Tabs...')
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
        check_links(data, config)    
                      
    # Create Tab Panels (what is shown when Tab is selected)
    logging.debug('Creating Tab Panels (Content)...')
    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=help).classes('w-full h-full fixed'):
            # Create one Tab for displaying help
            logging.debug(f"Creating Help Panel with the content of {config['help']['path']}...")
            with ui.tab_panel(help):                
                with open(config['help']['path'], 'r') as f: # open file 
                    with ui.card().classes('md:w-1/2 sm:w-full h-dvh pl-10 pb-20 bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                        ui.markdown(f.read()).classes('') 
            
            # Create one Grid for displaying everything
            logging.debug('Creating the show all grid...')
            with ui.tab_panel(everything):
                grid = create_grid(data, config)
        
            # Create One grid for each unique Category in the first Column
            # grids = [ui.aggrid]
            logging.debug('Creating one Grid for each Category...')
            for category in categories:
                category_data = data[data[config['data']['category']]==category]
                with ui.tab_panel(category):
                    grid = create_grid(category_data, config)
                    with ui.row():
                        grid.options['columnDefs'][0]['field']
                        ui.label().bind_text_from(grid, 'selected', lambda val: f'Current selection: {val}')
                        ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
                        ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))

    ui.dark_mode(True)
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    logging.debug('Finished. Starting UI...')
    ui.run(title=config['title'], favicon=config['favicon'], port=8081)

if __name__ in {"__main__", "__mp_main__"}:
    main()