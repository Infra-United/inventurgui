import pandas
from nicegui import ui
from pandas import DataFrame
from nicegui.ui import aggrid

"""This module implements functions to create AG Grids which display the data."""

def create_aggrid(data: DataFrame, config:dict) -> aggrid:
    """Returns an AG Grid displaying the given data in the given configuration.

    Args:
        data (DataFrame): The data to be displayed as a pandas DataFrame.
        config (dictionary): The configuration as a dictionary.

    Returns:
        aggrid: The AG Grid that results from the given Arguments.
    """   
    # Define Columns for AG Grids
    columnDefs = [
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':200, 'resizable': True, 'sort': 'asc', 'cellClassRules': {'text-secondary': 'x'}, 'cellStyle': {'padding-left':'10px'}},
        {'field': config['data']['desc'], 'minWidth': 250},   
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 50, 'maxWidth': 80, 'editable': True},
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
        
    # Create Grid with given Data
    return aggrid({
        'columnDefs': columnDefs,
        'defaultColDef': default_column_defs(),
        'rowData': data.to_dict('records'),
       # 'rowSelection': 'multiple',
        #'rowMultiSelectWithClick': True,
            },      
        html_columns=[0],
        theme='alpine-dark').classes('h-full').on('cellClicked', lambda event: dialog(event.args) if event.args['colId'] == 'has_link' else None)
    
    
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
