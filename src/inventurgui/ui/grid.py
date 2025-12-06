import pandas
from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments
from nicegui.html import source
from pandas import DataFrame
from nicegui.ui import aggrid

from inventurgui.io import warehouse

"""This module implements functions to create AG Grids which display the data."""

def create_aggrid(name:str, data: DataFrame, config:dict) -> AgGrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        name (str): name of the AG Grid to display
        data (DataFrame): The data to be displayed as a pandas DataFrame.
        config (dictionary): The configuration as a dictionary.
        cart (bool): Whether the grid is for the cart page. Defaults to False.

    Returns:
        aggrid: The AG Grid that results from the given Arguments.
    """
    cart = True if name == 'cart' else False
    # Define Columns for AG Grids
    columnDefs = [
        {'checkboxSelection': True , 'maxWidth': 35, 'filter': False},
        {'field': 'warehouse', 'headerName': '', 'minWidth': 100, 'maxWidth':200, 'hide': not cart},
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':200, 'resizable': True, 'sort': 'asc', 'cellClassRules': {'text-secondary': 'x'}, 'cellStyle': {'padding-left':'10px'}},
        {'field': config['data']['desc'], 'minWidth': 250},
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 50, 'maxWidth': 80, 'editable': cart, 'cellDataType': 'number'},
        {'field': config['data']['pack'], 'minWidth': 90}]

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

    theme = app.storage.user['grid_theme'] if app.storage.user.get('grid_theme') else 'alpine'
    # Create Grid with given Data
    grid =aggrid({
        'headerName': name,
        'selectionColumnDef': {'hide': True},
        'columnDefs': columnDefs,
        'defaultColDef': default_column_defs(),
        'rowData': data.to_dict('records'),
        'rowSelection': {'mode': 'multiRow', 'enableClickSelection': False, 'checkboxes': False,} if cart else 'multiple',
        'enterNavigatesVertically': True,
        'suppressCellFocus': True,
        'enterNavigatesVerticallyAfterEdit': True,
        'singleClickEdit': True,
        ':getRowId': '(params) => params.data.perma_id',
        'rowMultiSelectWithClick': True,
    },
        html_columns=[0],
        theme=theme).classes('sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)] w-screen')
    #grid.on('cellClicked', lambda: grid.run_grid_method(''))
    grid.on('rowSelected', lambda event: handle_selection(name, event))
    if cart:
        grid.on('firstDataRendered', lambda: grid.run_grid_method('selectAll'))
        grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeColumns', config['data']['desc']))
    else:
        for row in app.storage.user[name]:
            grid.on('firstDataRendered', lambda r=row: grid.run_row_method(r, 'setSelected', True))
        #grid.on('firstDataRendered', lambda rows=app.storage.user[name]: grid.run_grid_method('setGridOption', 'rowData', rows))
    grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeColumns', config['data']['desc']))
    grid.on('cellValueChanged') #TODO implement handler
    return grid

def handle_selection(name:str, event:GenericEventArguments):
    match event.args['source'] :
        case 'api':
            return
        case 'apiSelectAll':
            if name == 'cart':
                return
    if name == 'cart':
        name = event.args['data']['warehouse']
    row_id = event.args['rowId']
    if row_id not in app.storage.user[name]:
        app.storage.user[name].append(row_id)
    else:
        app.storage.user[name].remove(row_id)

    
def default_column_defs() -> dict:
    # Define default column properties for AG Grids
    defaultColDef:dict = {
        'flex': 1,
        'sortable': True,
        #'resizable': True,
        'filter': True,
        'floatingFilter': True}
    return defaultColDef

def dialog(event_args:dict):
    with ui.dialog() as dia:
        with ui.card():
            ui.label(text=f"{event_args['data']['Objekt']} ({event_args['data']['Art']})")
            ui.image(event_args['data']['Link'])
    return dia
