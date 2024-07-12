
from nicegui import ui
from pandas import DataFrame, isna
from pandas_ods_reader import read_ods

# Create HTML Links from URLs in the "Link" Column
def check_links(data: DataFrame):
    if data['Link'].isna().all(): 
        return
    else: 
        return data['Link'].where(data['Link'].isna(), other = '<a href="' + data['Link'] + '" target="_blank">' + "ℹ️" + '</a>', inplace=True)

def create_grid(data: DataFrame) -> None:
    # Define Columns for AG Grids
    columnDefs = [
    #    {'field': 'Thema', 'minWidth': 130},
      #  {'headerName': '', 'field': 'Url', 'filter': False, 'minWidth': 40, 'maxWidth': 40},
        {'field': 'Objekt', 'minWidth': 130, 'maxWidth':130, 'pinned': 'left', 'sort': 'asc', 'cellClassRules': {'text-secondary': 'x'}},
        {'field': 'Art', 'minWidth': 250},   
        {'field': 'Zahl', 'headerName': '', 'filter': False, 'minWidth': 40, 'maxWidth': 40},
        {'field': 'Packung', 'minWidth': 90},]
   
    # Define default column properties for AG Grids
    defaultColDef = {
        'flex': 1,
        'sortable': True,
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
    # read ods file to get inventory data
    path = "IU_Inventur.ods"    
    data = read_ods(path)
    check_links(data)
  
    # Create Tabs
    ui.colors(secondary='#FD916B', primary='#254060')
    with ui.header().classes('fixed p-0 m-0 bg-secondary text-primary') as header:
        with ui.tabs().classes('w-full') as tabs:
            # Create one Tab for showing Help
            hilfe = ui.tab(name='hilfe', label='', icon='help').classes('')
            # Create one Tab for showing everything
            alles = ui.tab(name='alles', label='Alles')
            # Create one Tab for each Kategorie
            kategorien:list[str] = sorted(data['Kategorie'].unique())
            for kategorie in kategorien:
                ui.tab(kategorie).classes('')
                      
    # Create Tab Panels (what is shown when Tab is selected)
    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=hilfe).classes('w-full h-full fixed'):
            
            # Create one Tab for displaying help
            with ui.tab_panel(hilfe):                
                with open('hilfe.md', 'r') as f: # open file 
                    with ui.card().classes('md:w-1/2 sm:w-full h-dvh pl-10 pb-20 bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                        ui.markdown(f.read()).classes('') 
            
            # Create one Grid for displaying everything
            with ui.tab_panel(alles):
                grid = create_grid(data)
            
            # Create One grid for each unique Category in the first Column
            # grids = [ui.aggrid]
            for kategorie in kategorien:
                kategorie_data = data[data['Kategorie']==kategorie]
                with ui.tab_panel(kategorie):
                    grid = create_grid(kategorie_data)
              #      with ui.row():
              #          ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
              #          ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'parent', True))

    ui.dark_mode(True)
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    ui.run(title='IU Inventur', favicon='favicon.jpeg')

if __name__ in {"__main__", "__mp_main__"}:
    main()