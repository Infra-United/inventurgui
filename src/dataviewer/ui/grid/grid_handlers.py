from contextlib import suppress

from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.dialog import Dialog
from nicegui.events import GenericEventArguments

from dataviewer.helper.config import settings
from dataviewer.io.cache import Cache
from dataviewer.io.selection import Selection
from dataviewer.ui.helper.markdown import render_markdown
from dataviewer.ui.helper.validators import validate_url


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


def handle_click(warehouse: Selection, grid: AgGrid, event: GenericEventArguments):
    columns = settings.columns
    data = event.args["data"]
    if any([data[columns["dance"]], data[columns["url"]]]) and columns["url"] == event.args["colId"]:
        info_popup(warehouse, event.args, grid)
    else:
        handle_select(warehouse.name, event, grid)


def info_popup(warehouse: Selection, event_args: dict, grid: AgGrid):
    data = event_args["data"]
    with ui.dialog(value=True) as dia:
        dia_content(dia, warehouse, data)
        dia.on("hide", lambda: update_row_data(data, grid, warehouse))
    return dia


@ui.refreshable
def dia_content(dia: Dialog, warehouse: Selection, data: dict[str, str], edit:bool=False):
    columns = settings.columns
    with dia.clear(), ui.card().classes("w-100 gap-2 items-center text-center py-4 px-2 text-bold"):
        #ui.button(icon='edit', on_click=lambda: dia_content.refresh(dia, warehouse, data, True)).classes("m-0")
        ui.label(text=f"{data.get(columns['title'])}")
        url = data.get(columns.get("url"))
        ui.link(url, url, new_tab=True).classes("w-80 m-4 text-justify") if url else None
        if edit:
            with ui.row(align_items="stretch").classes("w-80 gap-0 items-center text-center"):
                i = ui.input(
                    placeholder="URL:", value=url if url else "", validation=lambda v: validate_url(v, data)
                ).props("outlined")
                i.on("blur", lambda x=i: x.validate()).without_auto_validation().classes("w-65")
                del_link = ui.button(icon="delete", on_click=lambda: i.set_value("")).classes("h-14")
                del_link.on("click", lambda: data.update({columns.get("url"): ""}))
            ui.editor(value=data[columns["dance"]]).bind_value_to(data, columns["dance"])
        else:
            for column in ["artist", "desc", "comment", "dance"]:
                if not data.get(columns[column]):
                    continue
                md = render_markdown().classes(remove="text-justify pt-5", add="py-1")
                md.bind_content_from(data, columns[column], backward=lambda x: "" if x is None else x)
                md.bind_visibility(md, "content")


def update_row_data(data: dict[str, str], grid: AgGrid, warehouse: Selection):
    grid.run_row_method(data["index"], "setData", data)
    for key, value in data.items():
        warehouse.inventory[data["index"], key] = value
