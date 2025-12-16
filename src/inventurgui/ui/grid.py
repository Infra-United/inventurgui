import pandas
from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.ui import aggrid
from pandas import DataFrame

from inventurgui.helper.grid_handlers import handle_edit, max_amount, handle_select

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
    default_col_def: dict = {
        'sortable': True,
        'resizable': True,
        'filter': not cart,
        'floatingFilter': not cart}

    column_defs = [
        {'field': config['data']['object'], 'minWidth': 140, 'maxWidth':200, 'resizable': True, 'sort': 'asc', 'cellClassRules': {'text-primary': 'x', 'text-bold': 'x', 'tracking-wider':'x'}, 'cellStyle': {'padding-left':'10px'}},
        {'field': config['data']['desc'], 'minWidth': 250},
        {'field': config['data']['count'], 'headerName': '', 'filter': False, 'minWidth': 35, 'maxWidth': 50, 'editable': cart, 'cellEditorParams': '', 'cellDataType': 'number', 'pinned': 'left' if cart else '', 'cellClassRules': {'bg-primary': 'x > 1', 'text-secondary': 'x > 1'} if cart else ''},
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
        column_defs.insert(0, link_column)

    # Styling
    height = 'sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)]' if not cart else 'sm:h-[calc(100vh-104px)] h-[calc(100vh-102px)]'
    theme = app.storage.user['grid_theme'] if app.storage.user.get('grid_theme') else 'alpine'
    css = f'''{{background-color: {config['theme']['secondary']}}}'''
    ui.add_body_html(f'<style>.ag-row-hover .ag-cell  {css}</style>')
    ui.add_body_html(f'<style>.ag-row-selected .ag-cell  {css}</style>')

    # Create Grid with given Data
    grid =aggrid({
        'selectionColumnDef': {'hide': cart, 'maxWidth': 35, 'sortable': True},
        'columnDefs': column_defs,
        'defaultColDef': default_col_def,
        'rowData': data.to_dict('records'),
        'theme': theme,
        'rowSelection':  {'mode': 'multiRow',
                          'selectAll': 'filtered',
                          'ctrlASelectsRows': True,
                          'enableClickSelection': True,
                          'checkboxes': True,
                          'headerCheckbox': True,
                          'enableSelectionWithoutKeys': True,
                          } if not cart else '',
        'suppressRowHoverHighlight': cart,
        'enterNavigatesVertically': True,
        'readOnlyEdit': True,
        'invalidEditValueMode': 'block',
        'stopEditingWhenCellsLoseFocus': True,
        'suppressCellFocus': True,
        'enterNavigatesVerticallyAfterEdit': True,
        'singleClickEdit': True,
        ':getRowId': '(params) => params.data.perma_id',
    },
        html_columns=[0],
        theme=theme).classes(f'{height}')

    # Handle events
    grid.on('rowSelected', lambda event: handle_select(name, event))
    if not cart:
        for row in app.storage.user[name]:
                grid.on('firstDataRendered', lambda r=row: grid.run_row_method(r, 'setSelected', True))
    else:
        for row in app.storage.user['amounts'][name]:
            grid.on('firstDataRendered', lambda r=row: grid.run_row_method(r, 'setDataValue', config['data']['count'], app.storage.user['amounts'][name].get(r)[0]))
    #if int(app.storage.user.get('screen').get('width')) < 640:
    grid.on('firstDataRendered', lambda: grid.run_grid_method('autoSizeColumns'))
    grid.on('cellEditingStarted', lambda event: max_amount(name, event))
    grid.on('cellEditRequest', lambda event: handle_edit(grid, name, event))
    #grid.on('cellValueChanged', lambda event: handle_edit(name, event))
    ui.on('resize', lambda: grid.update(), throttle=0.8, trailing_events=True)
    return grid

def dialog(event_args:dict):
    with ui.dialog() as dia:
        with ui.card():
            ui.label(text=f"{event_args['data']['Objekt']} ({event_args['data']['Art']})")
            ui.image(event_args['data']['Link'])
    return dia
