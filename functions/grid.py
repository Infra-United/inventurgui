# Create HTML link from URLs in the "Link" Column
from pandas import DataFrame
from nicegui import ui

def check_links(data: DataFrame, config:dict):
    link = data[config['links']['column']]
    if link.isna().all(): 
        return
    else: 
        return link.where(link.isna(), other = '<a href="' + link + '" target="_blank">' + "ℹ️" + '</a>', inplace=True)

def create_grid(data: DataFrame, config:dict) -> None:
    # Define Columns for AG Grids
    columnDefs = [
        {'headerName': '', 'field': config['links']['column'], 'filter': False, 'minWidth': 40, 'maxWidth': 40},
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':200, 'resizable': True, 'pinned': 'left', 'sort': 'asc', 'cellClassRules': {'text-secondary': 'x'}},
        {'field': config['data']['desc'], 'minWidth': 250},   
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 50, 'maxWidth': 80},
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
        'rowSelection': 'multiple',
        'rowMultiSelectWithClick': True,
        },      
        html_columns=[0],
        theme='alpine-dark').classes('h-5/6 #pb-10')
    