from contextlib import suppress

from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.dialog import Dialog
from nicegui.events import GenericEventArguments

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.images import upload_img, delete_img
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.markdown import render_markdown
from inventurgui.ui.helper.validators import validate_url


async def update_amount(grid: AgGrid, warehouse: Warehouse, event: GenericEventArguments):
    with suppress(KeyError):
        if event.args["rowPinned"]:
            return
    row_id = event.args["rowId"]
    new_value = event.args.get("newValue")
    data: dict = event.args["data"]
    if new_value > data[settings.columns["total"]]:
        ui.notify(i18n.get("cart.too_many"), position="center", type="negative", color="secondary")
        return
    Cache.amounts(warehouse.name).update({row_id: int(new_value)})
    data.update({event.args["colId"]: new_value})
    with suppress(TypeError):
        data[settings.columns["total_weight"]] = int(new_value) * data[settings.columns["weight"]]
    await grid.run_row_method(row_id, "setData", data)
    Cache.set_weight(warehouse.name, await warehouse.total_weight())


def handle_select(name: str, event: GenericEventArguments, grid: AgGrid):
    with suppress(KeyError):
        if event.args["source"] == "api":
            return
    row_id = event.args["rowId"]
    if int(row_id) not in Cache.selected(name):
        Cache.selected(name).append(int(row_id))
        app.storage.user["Total"] += 1
        grid.run_row_method(row_id, "setSelected", True)
    else:
        Cache.selected(name).remove(int(row_id))
        app.storage.user["Total"] -= 1
        grid.run_row_method(row_id, "setSelected", False)


def handle_click(warehouse: Warehouse, grid: AgGrid, event: GenericEventArguments):
    columns = settings.columns
    data = event.args["data"]
    admin = authenticate_user()
    if (
        any([data[columns["image"]], data[columns["comment"]], data[columns["url"]]])
        and event.args["colId"] == columns["image"] and not admin
    ):
        info_popup(warehouse, event.args, grid)
    elif admin and event.args["colId"] == columns["image"]:
        info_popup(warehouse, event.args, grid)
    else:
        handle_select(warehouse.name, event, grid) if not admin else None

def info_popup(warehouse: Warehouse, event_args: dict, grid: AgGrid):
    admin = authenticate_user()
    data = event_args["data"]
    with ui.dialog(value=True) as dia:
        dia_content(dia, warehouse, data, admin)
        dia.on("hide", lambda: update_row_data(data, grid, warehouse))
    return dia

@ui.refreshable
def dia_content(dia:Dialog, warehouse: Warehouse, data: dict[str, str], admin: bool):
    columns = settings.columns
    with dia.clear(), ui.card().classes("w-100 gap-2 items-center text-center py-4 text-bold"):
        ui.label(text=f"{data.get(columns['object'])}")
        if src:=data.get(columns["image"]):
            img = ui.interactive_image(src)
        if admin:
            up = ui.upload(label=i18n.get("admin.upload"), auto_upload=True)
            up.on_upload(lambda e: upload_img(warehouse.name, e, data))
            up.props('accept="image/*" flat bordered max-files=1 capture=environment')
        url = data.get(columns.get("url"))
        ui.link(url, url, new_tab=True) if url else None
        if admin:
            i = ui.input(placeholder="URL:", value=url if url else "",
                         validation=lambda v: validate_url(v,data)).props("outlined")
            i.on("blur", lambda x=i: x.validate()).without_auto_validation().classes("w-80")
            ui.editor(value=data[columns["comment"]]).bind_value_to(data, columns["comment"])
            if data.get(columns["image"]):
                with img:
                    up.on_upload(lambda: img.force_reload())
                    del_btn = ui.button(icon="delete").classes("absolute top-0 right-0")
                    del_btn.on('click', lambda: delete_img(data))
                    del_btn.on('click', lambda: img.delete())
        else:
            md = render_markdown().classes(remove="text-justify")
            md.bind_content_from(data, columns["comment"], backward=lambda x: "" if x is None else x)
            md.bind_visibility(md, "content")

def update_row_data(data: dict[str, str], grid: AgGrid, warehouse: Warehouse):
    grid.run_row_method(data["index"], "setData", data)
    for key, value in data.items():
        warehouse.inventory[data["index"], key] = value