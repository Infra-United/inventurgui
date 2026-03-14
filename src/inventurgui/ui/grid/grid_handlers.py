import re
from contextlib import suppress
from pathlib import Path

import polars as pl
from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.events import GenericEventArguments, UploadEventArguments
from polars import DataFrame

from inventurgui.helper.config import settings, URL_REGEX
from inventurgui.helper.i18n import i18n
from inventurgui.helper.paths import get_path
from inventurgui.io.cache import Cache
from inventurgui.ui.auth import authenticate_user


def update_row_data(df: DataFrame, data: dict, grid:AgGrid, event_args: dict):
    if not "rowPinned" in event_args:
        grid.run_row_method(data.get('perma_id'), "setData", data)
        df.update(pl.from_dict(data), on='perma_id') # TODO handle correctly
    else:
        print(data)
        ui.notify("pinned") # TODO add new row with data

def update_amount(grid: AgGrid, name: str, event: GenericEventArguments):
    row_id = event.args["rowId"]
    new_value = event.args.get("newValue")
    data: dict = event.args["data"]
    total = data[settings.columns['total']]
    if new_value > total:
        ui.notify(i18n.get("cart.too_many"), position="center", type="negative", color="secondary")
        return
    Cache.amounts(name).update({row_id: int(new_value)})
    data.update({event.args['colId']: new_value})
    data[settings.columns['total_weight']] = int(new_value) * data[settings.columns['weight']]
    grid.run_row_method(row_id, "setData", data)

def handle_select(name: str, event: GenericEventArguments, grid:AgGrid):
    with suppress(KeyError):
        if event.args["source"] == "api":
            return
    row_id = event.args["rowId"]
    if int(row_id) not in Cache.selected(name):
        Cache.selected(name).append(int(row_id))
        app.storage.user["Total"] += 1
        grid.run_row_method(row_id, 'setSelected', True)
    else:
        Cache.selected(name).remove(int(row_id))
        app.storage.user["Total"] -= 1
        grid.run_row_method(row_id, 'setSelected', False)

def handle_click(name: str, grid:AgGrid, event: GenericEventArguments, df: DataFrame):
    if event.args['colId'] == settings.columns['image']:
        info_popup(name, event.args, df, grid)
    else:
        handle_select(name, event, grid) if not authenticate_user() else None

def info_popup(name: str, event_args: dict, df: DataFrame, grid:AgGrid):
    admin = authenticate_user()
    async def upload_img(event: UploadEventArguments):
        path = get_path(f"{name}/{data[settings.columns['object']]}_{data['perma_id']}", "images")
        path.unlink(missing_ok=True)
        await event.file.save(path)
        dia_content()

    async def delete_img(path: Path):
        path.unlink()
        data[columns['image']] = ''
        update_row_data(df, data, grid, event_args)
        dia_content()

    def dia_content():
        with (dia.clear(), ui.card().classes("w-100 gap-2 items-center text-justify py-4 text-bold")):
            if data is not None:
                ui.label(text=f"{data.get(columns['object'])}")
            path = get_path(f"{name}/{data.get(columns['object'])}", "images")
            if path.is_file():
                img_url = '/images/' + f"{name}/{data.get(columns['object'])}"
                img = ui.interactive_image(img_url)
                data[columns['image']] = img_url
            else:
                match = re.search(URL_REGEX, data[columns['image']]) if data.get(columns['image']) else None
                ui.interactive_image(match.group("url")) if match else None
            md = ui.markdown().classes(
                "p-5 mx-auto hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180"
            )
            md.bind_content_from(data, columns['comment'], backward=lambda x: '' if x is None else x)
            md.bind_visibility(md, 'content')
            url = data.get(columns.get("url"))
            ui.link(url, url, new_tab=True) if url else None
            if admin:
                if not path.is_file():
                    up = ui.upload(label=i18n.get('admin.upload'), auto_upload=True, on_upload=lambda e: upload_img(e))
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
        if admin:
            dia.on('hide', lambda: update_row_data(df, data, grid, event_args))
    return dia
