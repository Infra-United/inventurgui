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
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':200, 'resizable': True, 'pinned': 'left', 'sort': 'asc', 'cellClassRules': {'text-secondary': 'x'}, 'cellStyle': {'padding-left':'10px'}},
        {'field': config['data']['desc'], 'minWidth': 250},   
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 50, 'maxWidth': 80},
        {'field': config['data']['pack'], 'minWidth': 90}]
    
    if config['links']['display']:
        columnDefs.insert(0,{'headerName': '', 'field': config['links']['name'], 'filter': False, 'minWidth': 30, 'maxWidth': 30, 'cellStyle': {'padding-left':'2.5px', 'padding-right': '2.5px'}})
    
    # Create Grid with given Data
    return aggrid({
        'columnDefs': columnDefs,
        'defaultColDef': default_column_defs(),
        'rowData': data.to_dict('records'),
        'rowSelection': 'multiple',
        'rowMultiSelectWithClick': True,
            },      
        html_columns=[0],
        theme='alpine-dark').classes('h-5/6')
    
    
def default_column_defs() -> dict:
    # Define default column properties for AG Grids
    defaultColDef:dict = {
        'flex': 1,
        'sortable': True,
        #'resizable': True,
        'filter': True,
        'floatingFilter': True}
    return defaultColDef


def handle_links(data: DataFrame, links:str) -> DataFrame:
    """Checks for data in the given DataFrame and convert them to HTML <a> tags inside the same DataFrame. 
    Args:
        data (DataFrame): The pandas DataFrame that contains the links column.
        links (string): The name of the column with links.
    Returns:
        DataFrame: The modified links column as a pandas Dataframe.
    """    
    links = data[links]
    #(grid.options['columnDefs'][0]['field'])
    if links.isna().all():
        return links
    else: # Replace URLs in the data column with HTML strings and return it
        return links.where(links.isna(), other = '<a href="' + links + '" target="_blank">' + '<span style="font-size: 24px;">ℹ️</span>' + '</a>', inplace=True)
        