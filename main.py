
import logging
from nicegui import ui
from pandas import DataFrame, isna
from pandas_ods_reader import read_ods
import yaml
import argparse
from cli import get_args

# Create HTML link from URLs in the "Link" Column
def check_links(data: DataFrame, config:dict):
    link = data[config['links']['column']]
    if link.isna().all(): 
        return
    else: 
        return link.where(link.isna(), other = '<a href="' + link + '" target="_blank">' + "ℹ️" + '</a>', inplace=True)

def create_grid(data: DataFrame, config:dict) -> None:
    # Define Columns for AG Grids
    columnDefs = [
    #    {'field': 'Thema', 'minWidth': 130},
        {'headerName': '', 'field': 'Url', 'filter': False, 'minWidth': 40, 'maxWidth': 40},
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':140, 'pinned': 'left', 'sort': 'asc', 'cellClassRules': {'text-secondary': 'x'}},
        {'field': config['data']['desc'], 'minWidth': 250},   
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 40, 'maxWidth': 40},
        {'field': config['data']['pack'], 'minWidth': 90},]
   
    # Define default column properties for AG Grids
    defaultColDef = {
        'flex': 1,
        'sortable': True,
        #'resizable': True,
        'filter': True,
        'floatingFilter': True}
    
    # Create Grid with given Data
    return ui.aggrid({
        'columnDefs': columnDefs,
        'defaultColDef': defaultColDef,
        'rowData': data.to_dict('records'),
        #'rowSelection': 'multiple',
        #'rowMultiSelectWithClick': True,
        },      
        html_columns=[0],
        theme='alpine-dark').classes('h-screen pb-10')
    
def main():
     # get Arguments from Command-Line and set log-level
    args:dict = get_args()
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.info(f"Args: {args}")
    
    # get Config from yml file
    logging.debug('Loading config file...')
    try:
        with open(args.config_file, 'r') as f: 
            config:dict = yaml.load(f, Loader=yaml.FullLoader) 
    except FileNotFoundError:
        logging.exception('Config File not Found:', args.config_file); exit()
    
    # read ods file to get inventory data
    path = config['data']['path']    
    data = read_ods(path)
    if config['links']['display']:
        check_links(data, config)
        

        
    # Create Tabs
    ui.colors(secondary=config['colors']['secondary'], primary=config['colors']['primary'])
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
                      
    # Create Tab Panels (what is shown when Tab is selected)
    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=help).classes('w-full h-full fixed'):
            
            # Create one Tab for displaying help
            with ui.tab_panel(help):                
                with open(config['help']['path'], 'r') as f: # open file 
                    with ui.card().classes('md:w-1/2 sm:w-full h-dvh pl-10 pb-20 bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                        ui.markdown(f.read()).classes('') 
            
            # Create one Grid for displaying everything
            with ui.tab_panel(everything):
                grid = create_grid(data, config)
            
            # Create One grid for each unique Category in the first Column
            # grids = [ui.aggrid]
            for category in categories:
                category_data = data[data[config['data']['category']]==category]
                with ui.tab_panel(category):
                    grid = create_grid(category_data, config)
              #      with ui.row():
              #          ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
              #          ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'parent', True))

    ui.dark_mode(True)
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    ui.run(title=config['title'], favicon=config['favicon'])

if __name__ in {"__main__", "__mp_main__"}:
    main()