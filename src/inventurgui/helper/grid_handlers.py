from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments
from nicegui.observables import ObservableDict

from inventurgui.helper.config import config
from inventurgui.helper.storage import Storage
from inventurgui.ui.auth import authenticate_user


def handle_edit(grid: AgGrid, name: str, event: GenericEventArguments):
    row_id = event.args["rowId"]
    new_value = event.args.get("newValue")
    edited_rows: ObservableDict = Storage.amounts().get(name)
    if row_id not in edited_rows.keys():
        initial_value = event.args["oldValue"]
        if new_value > initial_value and not authenticate_user():
            ui.notify(config["cart"]["invalid_edit"], position="center", type="negative", color="secondary")
            return
        edited_rows.update({row_id: [new_value, initial_value]})
    else:
        if new_value > edited_rows[row_id][1] and not authenticate_user():
            ui.notify(config["cart"]["invalid_edit"], position="center", type="negative", color="secondary")
            return
        edited_rows[row_id][0] = new_value
    row_data: dict = event.args["data"]
    row_data.update({event.args['colId']: new_value})
    grid.run_row_method(row_id, "setData", row_data)


def handle_select(name: str, event: GenericEventArguments):
    match event.args["source"]:
        case "api":
            return
    row_id = event.args["rowId"]
    if row_id not in Storage.selected(name):
        Storage.selected(name).append(row_id)
        app.storage.user["Total"] += 1
    else:
        Storage.selected(name).remove(row_id)
        app.storage.user["Total"] -= 1

def handle_click(name: str, grid:AgGrid, event: GenericEventArguments):
    if event.args['colId'] == config['data']['image']:
        info_popup(event.args)
    else:
        row = event.args['rowId']
        is_selected = False if row in Storage.selected(name) else True
        grid.run_row_method(row, 'setSelected', is_selected)


def info_popup(event_args: dict):
    with ui.dialog() as dia:
        with ui.card().tight().classes("w-full gap-2 items-center py-4 text-bold"):
            ui.label(text=f"{event_args['data']['Objekt']} ({event_args['data']['Art']})")
            source = event_args["data"]["Link"]
            if source:
                ui.image()
            if authenticate_user():
                if not source:
                    ui.upload().props('accept="image/*" capture=environment')
                else:
                    ui.button(icon='delete')
    return dia
