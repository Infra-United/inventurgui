import pandas
from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments
from nicegui.ui import aggrid
from pandas import DataFrame

"""This module implements functions to create AG Grids which display the data."""

def create_aggrid(name:str, data: DataFrame, config:dict, cart:bool=False) -> AgGrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        name (str): name of the AG Grid to display
        data (DataFrame): The data to be displayed as a pandas DataFrame.
        config (dictionary): The configuration as a dictionary.
        cart (bool): Whether the grid is for the cart page. Defaults to False.

    Returns:
        aggrid: The AG Grid that results from the given Arguments.
    """
    # Define Columns for AG Grids
    columnDefs = [
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':200, 'resizable': True, 'sort': 'asc', 'cellClassRules': {'text-primary': 'x'}, 'cellStyle': {'padding-left':'10px'}},
        {'field': config['data']['desc'], 'minWidth': 250},
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 35, 'maxWidth': 50, 'editable': cart, 'cellDataType': 'number', 'pinned': 'left' if cart else ''},
        {'field': config['data']['pack'], 'minWidth': 90, 'maxWidth': 100, 'pinned': 'left' if cart else ''}]

    if config['links']['display']:
        # Function to replace https links with HTML string
        def replace_https_with_html(link):
            if pandas.isna(link):
                return link  # Return NaN as is
            if link.startswith('http'):
                return f'<span style="font-size: 24px;">ℹ️</span>'
            return link  # Return the link as is if it doesn't start with https://

        # Apply the function to the 'links' column
        pandas.options.mode.copy_on_write = True
        data['has_link'] = data[config['links']['column']].apply(replace_https_with_html)
        link_column = {'headerName': '', 'field': 'has_link', 'filter': False, 'minWidth': 50, 'maxWidth': 50}
        columnDefs.insert(0, link_column)

    height = 'sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)]' if not cart else 'sm:h-[calc(100vh-114px)] h-[calc(100vh-110px)]'
    theme = app.storage.user['grid_theme'] if app.storage.user.get('grid_theme') else 'alpine'
    # Create Grid with given Data
    grid =aggrid({
        'selectionColumnDef': {'hide': cart, 'maxWidth': 35, 'sortable': True},
        'columnDefs': columnDefs,
        'defaultColDef': default_column_defs(cart),
        'rowData': data.to_dict('records'),
        'rowSelection':  {'mode': 'multiRow',
                          'selectAll': 'filtered',
                          'ctrlASelectsRows': True,
                          'enableClickSelection': True,
                          'checkboxes': True,
                          'headerCheckbox': True,
                          'enableSelectionWithoutKeys': True,
                          } if not cart else '',
        'enterNavigatesVertically': True,
        'suppressCellFocus': True,
        'enterNavigatesVerticallyAfterEdit': True,
        'singleClickEdit': True,
        ':getRowId': '(params) => params.data.perma_id',
    },
        html_columns=[0],
        theme=theme).classes(f'{height} lg:w-[calc(100dvw-250px)] max-lg:w-screen')
    grid.on('rowSelected', lambda event: handle_selection(name, event))
    for row in app.storage.user[name]:
        if not cart:
            grid.on('firstDataRendered', lambda r=row: grid.run_row_method(r, 'setSelected', True))
    if int(app.storage.user.get('screen').get('width')) < 640:
        grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeColumns'))
    grid.on('cellValueChanged') #TODO implement handler
    ui.on('resize', lambda: grid.update(), throttle=0.4)
    return grid

def handle_selection(name:str, event:GenericEventArguments):
    match event.args['source'] :
        case 'api':
            return
    row_id = event.args['rowId']
    if row_id not in app.storage.user[name]:
        app.storage.user[name].append(row_id)
        app.storage.user['Total'] += 1
    else:
        app.storage.user[name].remove(row_id)
        app.storage.user['Total'] -= 1

    
def default_column_defs(cart:bool) -> dict:
    # Define default column properties for AG Grids
    defaultColDef:dict = {
        'flex': 1,
        'sortable': True,
        #'resizable': True,
        'filter': not cart,
        'floatingFilter': not cart}
    return defaultColDef

def dialog(event_args:dict):
    with ui.dialog() as dia:
        with ui.card():
            ui.label(text=f"{event_args['data']['Objekt']} ({event_args['data']['Art']})")
            ui.image(event_args['data']['Link'])
    return dia
