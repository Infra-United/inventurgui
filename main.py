from nicegui import ui
from pandas import DataFrame
from pandas_ods_reader import read_ods

def create_topic_list(switch: ui.switch, data: DataFrame, kategorie: str="Alles"):
    with ui.row().bind_visibility_from(switch, 'value'):
        ui.label(f"Filterbare Themen in {kategorie}:").classes('bg-secondary text-primary block p-2 rounded')
        themen = sorted(data['Thema'].unique())
        for thema in themen:
            ui.label(thema).classes('bg-primary block p-2 rounded')

def create_grid(data: DataFrame, alles: bool) -> None:
    # Define Columns for AG Grids
    columnDefs = [
        {'field': 'Thema', 'minWidth': 130},
        {'field': 'Objekt', 'minWidth': 130},
        {'field': 'Art', 'minWidth': 130},   
        {'field': 'Zahl', 'headerName': 'Anzahl', 'minWidth': 20},
        {'field': 'Packung', 'minWidth': 80}]
    if alles:
            columnDefs.insert(0, {'field': 'Kategorie', 'minWidth': 130})
    
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
    }, theme='alpine-dark').classes('h-full')
        

def main():
    # read ods file to get inventory data
    path = "IU Inventur.ods"    
    data = read_ods(path)
    
    # Drop "Regal" Column and "IU Werkeln" Entries
    # data.drop('Regal', axis=1, inplace=True)
    data.drop(data[data['Kategorie']=='IU Werkeln'].index, inplace=True)
    
    # Create Tabs
    ui.colors(secondary='#FD916B', primary='#254060')
    with ui.header().classes('fixed p-0 m-0 bg-secondary text-primary') as header:
        with ui.tabs().classes('w-full') as tabs:
            # Create one Tab for showing Help
            # Create one Tab for everything
            alles = ui.tab('Alles').classes('')
            # Create one Tab for each Kategorie
            kategorien:list[str] = sorted(data['Kategorie'].unique())
            for kategorie in kategorien:
                ui.tab(kategorie).classes('')
            zeigethemen = ui.switch(f"Zeige verfügbare Themen", value=False).classes('')
            
    # Create Tab Panels (what is shown when Tab is selected)
    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=alles).classes('w-full h-full fixed'):
            # Create one for displaying everything
            with ui.tab_panel(alles):                
                create_topic_list(zeigethemen, data)
                create_grid(data, True)
            
            # Create One for each Kategorie
            grids = [ui.aggrid]
            for kategorie in kategorien:
                kategorie_data = data[data['Kategorie']==kategorie]
                with ui.tab_panel(kategorie):
                    create_topic_list(zeigethemen, kategorie_data, kategorie)
                    grid = create_grid(kategorie_data, False)

    ui.dark_mode(True)
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    ui.run(title='IU Anfrage-Tool', favicon='favicon.jpeg')

if __name__ in {"__main__", "__mp_main__"}:
    main()