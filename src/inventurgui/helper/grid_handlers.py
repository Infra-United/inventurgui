from contextlib import suppress

from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments
from nicegui.observables import ObservableDict

from inventurgui.helper.config import config


def max_amount(name:str, event:GenericEventArguments):
    with suppress(TypeError):
        amount = app.storage.user['amounts'][name].get(event.args['rowId'])[1]
        ui.notify(f"Maximum: {amount}", position='center', type='info', color='secondary')

def handle_edit(grid:AgGrid, name:str, event:GenericEventArguments):
    row_id = event.args['rowId']
    new_value = event.args['newValue']
    edited_rows:ObservableDict = app.storage.user['amounts'][name]
    if not row_id in edited_rows.keys():
        initial_value = event.args['oldValue']
        if new_value > initial_value:
            ui.notify(config['cart']['invalid_edit'], position='center', type='negative', color='secondary')
            return
        edited_rows.update({row_id: [new_value, initial_value]})
    else:
        if new_value > edited_rows[row_id][1]:
            ui.notify(config['cart']['invalid_edit'], position='center', type='negative', color='secondary')
            return
        edited_rows[row_id][0] = new_value
    row_data:dict = event.args['data']
    row_data.update({config['data']['count']: new_value})
    grid.run_row_method(row_id,'setData', row_data)

def handle_select(name:str, event:GenericEventArguments):
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