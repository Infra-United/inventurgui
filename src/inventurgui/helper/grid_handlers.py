from os import mkdir
from pathlib import Path

from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments, UploadEventArguments
from nicegui.observables import ObservableDict
from pandas import DataFrame

from inventurgui.helper.config import config, get_path
from inventurgui.io.cache import Cache
from inventurgui.ui.auth import authenticate_user


def handle_edit(grid: AgGrid, name: str, event: GenericEventArguments):
    row_id = event.args["rowId"]
    new_value = event.args.get("newValue")
    edited_rows: ObservableDict = Cache.amounts().get(name)
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
    if row_id not in Cache.selected(name):
        Cache.selected(name).append(row_id)
        app.storage.user["Total"] += 1
    else:
        Cache.selected(name).remove(row_id)
        app.storage.user["Total"] -= 1

def handle_click(name: str, grid:AgGrid, event: GenericEventArguments, df: DataFrame):
    if event.args['colId'] == config['data']['image']:
        info_popup(name, event.args, df, grid)
    else:
        row = event.args['rowId']
        is_selected = False if row in Cache.selected(name) else True
        grid.run_row_method(row, 'setSelected', is_selected)

def info_popup(name: str, event_args: dict, df: DataFrame, grid:AgGrid):
    async def upload_img(event: UploadEventArguments):
        w_dir = get_path(f"images/{name}")
        if not w_dir.is_dir():
            mkdir(w_dir)
        path = Path(f"{w_dir}/{data[config['data']['object']]}_{data['perma_id']}")
        path.unlink(missing_ok=True)
        await event.file.save(path)
        dia_content()

    async def delete_img(path: Path):
        path.unlink()
        data[conf['image']] = ''
        update_row_data(df, data, grid)
        dia_content()

    def dia_content():
        with (dia.clear(), ui.card().classes("w-100 gap-2 items-center py-4 text-bold")):
            if data is not None:
                ui.label(text=f"{data[conf['object']]} ({data[conf['desc']]})")
            path = get_path(f"images/{name}/{data[conf['object']]}_{data['perma_id']}")
            url = '/images/' + f"{name}/{data[conf['object']]}_{data['perma_id']}"
            if path.is_file():
                img = ui.interactive_image(url)
                data[conf['image']] = url
            md = ui.markdown().classes(
                "p-10 pt-5 mx-auto text-justify hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180"
            )
            md.bind_content_from(data, conf['comment'], backward=lambda x: '' if x is None else x)
            md.bind_visibility(md, 'content')
            if authenticate_user():
                if not path.is_file():
                    up = ui.upload(label=config['admin']['upload'], auto_upload=True, on_upload=lambda e: upload_img(e))
                    up.props('accept="image/*" capture=environment')
                else:
                    img.force_reload() # To prevent use of cached image instead of newly uploaded one
                    with img:
                        ui.button(icon='delete', on_click=lambda e: delete_img(path)).classes("absolute bottom-0 right-0")
                ui.editor(value=data[conf['comment']]).bind_value_to(data, conf['comment'])

    data = event_args['data']
    conf = config["data"]
    with ui.dialog(value=True) as dia:
        dia_content()
        dia.on('hide', lambda: update_row_data(df, data, grid))
    return dia

def update_row_data(df: DataFrame, data: dict, grid:AgGrid):
    grid.run_row_method(data['perma_id'], "setData", data)
    df.loc[data['perma_id']] = data