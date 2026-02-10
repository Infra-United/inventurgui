from contextlib import suppress
from os import mkdir
from pathlib import Path

from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments, UploadEventArguments
from pandas import DataFrame

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.io.cache import Cache
from inventurgui.ui.auth import authenticate_user


def update_row_data(df: DataFrame, data: dict, grid:AgGrid, event_args: dict):
    if not "rowPinned" in event_args:
        grid.run_row_method(data.get('perma_id'), "setData", data)
        df.loc[data.get('perma_id')] = data
    else:
        print(data)
        ui.notify("pinned") # TODO add new row with data

def handle_edit(grid: AgGrid, name: str, event: GenericEventArguments, df:DataFrame):
    ui.notify("editing")

def handle_add_delete(grid: AgGrid, name: str, event: GenericEventArguments, df: DataFrame):
    if "rowPinned" in event.args:
        ui.notify("adding")
    else:
        ui.notify("deleting")

def update_amount(grid: AgGrid, name: str, event: GenericEventArguments):
    row_id = event.args["rowId"]
    new_value = event.args.get("newValue")
    data: dict = event.args["data"]
    total = data["total"]
    if new_value > total:
        ui.notify(settings["cart"]["invalid_edit"], position="center", type="negative", color="secondary")
        return
    Cache.amounts().get(name).update({row_id: [new_value, total]})
    data.update({event.args['colId']: new_value})
    grid.run_row_method(row_id, "setData", data)

def handle_select(name: str, event: GenericEventArguments, grid:AgGrid):
    with suppress(KeyError):
        if event.args["source"] == "api":
            return
    row_id = event.args["rowId"]
    if row_id not in Cache.selected(name):
        Cache.selected(name).append(row_id)
        app.storage.user["Total"] += 1
        grid.run_row_method(row_id, 'setSelected', True)
    else:
        Cache.selected(name).remove(row_id)
        app.storage.user["Total"] -= 1
        grid.run_row_method(row_id, 'setSelected', False)

def handle_click(name: str, grid:AgGrid, event: GenericEventArguments, df: DataFrame):
    if event.args['colId'] == settings.columns['image']:
        info_popup(name, event.args, df, grid)
    elif event.args['colId'] == 'add_delete':
        handle_add_delete(grid, name, event, df)
    else:
        handle_select(name, event, grid) if not authenticate_user() else None

def info_popup(name: str, event_args: dict, df: DataFrame, grid:AgGrid):
    async def upload_img(event: UploadEventArguments):
        w_dir = get_path(f"images/{name}")
        if not w_dir.is_dir():
            mkdir(w_dir)
        path = Path(f"{w_dir}/{data[settings.columns['object']]}_{data['perma_id']}")
        path.unlink(missing_ok=True)
        await event.file.save(path)
        dia_content()

    async def delete_img(path: Path):
        path.unlink()
        data[columns['image']] = ''
        update_row_data(df, data, grid)
        dia_content()

    def dia_content():
        with (dia.clear(), ui.card().classes("w-100 gap-2 items-center py-4 text-bold")):
            if data is not None:
                ui.label(text=f"{data.get(columns['object'])} ({data.get(columns['type'])})")
            path = get_path(f"images/{name}/{data.get(columns['object'])}_{data.get('perma_id')}")
            url = '/images/' + f"{name}/{data.get(columns['object'])}_{data.get('perma_id')}"
            if path.is_file():
                img = ui.interactive_image(url)
                data[columns['image']] = url
            md = ui.markdown().classes(
                "p-10 pt-5 mx-auto text-justify hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180"
            )
            md.bind_content_from(data, columns['comment'], backward=lambda x: '' if x is None else x)
            md.bind_visibility(md, 'content')
            if authenticate_user():
                if not path.is_file():
                    up = ui.upload(label=settings.admin['upload'], auto_upload=True, on_upload=lambda e: upload_img(e))
                    up.props('accept="image/*" capture=environment')
                else:
                    img.force_reload() # To prevent use of cached image instead of newly uploaded one
                    with img:
                        ui.button(icon='delete', on_click=lambda e: delete_img(path)).classes("absolute bottom-0 right-0")
                ui.editor(value=data.get(columns['comment'])).bind_value_to(data, columns['comment'])

    data = event_args['data']
    columns = settings.columns
    with ui.dialog(value=True) as dia:
        dia_content()
        dia.on('hide', lambda: update_row_data(df, data, grid, event_args))
    return dia
