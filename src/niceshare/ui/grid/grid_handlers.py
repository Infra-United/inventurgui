from contextlib import suppress

import polars as pl
from nicegui import app, ui
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.dialog import Dialog
from nicegui.events import GenericEventArguments
from polars import DataFrame

from niceshare.helper.config import settings
from niceshare.helper.i18n import i18n
from niceshare.io.cache import Cache
from niceshare.io.selection import Selection
from niceshare.ui.helper.markdown import render_markdown
from niceshare.ui.helper.validators import validate_url


async def update_amount(grid: AgGrid, name: str, df: DataFrame, event: GenericEventArguments):
    with suppress(KeyError):
        if event.args["rowPinned"]:
            return
    row_id = event.args["rowId"]
    new_value = event.args.get("newValue")
    data: dict = event.args["data"]
    if new_value > data[settings.columns["total"]]:
        ui.notify(i18n.get("cart.too_many"), position="center", type="negative", color="secondary")
        return
    Cache.amounts(name).update({row_id: int(new_value)})
    data.update({event.args["colId"]: new_value})
    with suppress(TypeError):
        data[settings.columns["total_weight"]] = int(new_value) * data[settings.columns["weight"]]
    await grid.run_row_method(row_id, "setData", data)


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


def handle_click(selection: Selection, grid: AgGrid, event: GenericEventArguments):
    columns = settings.columns
    data = event.args["data"]
    if (
        any([data[columns["image"]], data[columns["comment"]], data[columns["url"]]])
        and event.args["colId"] == columns["image"]
    ):
        info_popup(selection, event.args, grid)
    elif event.args["colId"] == columns["image"]:
        info_popup(selection, event.args, grid)
    else:
        handle_select(selection.name, event, grid)


def info_popup(selection: Selection, event_args: dict, grid: AgGrid):
    data = event_args["data"]
    with ui.dialog(value=True) as dia:
        dia_content(dia, selection.name, data)
        dia.on("hide", lambda: update_row_data(data, grid, selection))
    return dia


@ui.refreshable
def dia_content(dia: Dialog, name: str, data: dict[str, str]):
    columns = settings.columns
    with dia.clear(), ui.card().classes("w-100 gap-2 items-center text-center py-4 text-bold"):
        ui.label(text=f"{data.get(columns['object'])}")
        if src := data.get(columns["image"]):
            img = ui.interactive_image(src)
        url = data.get(columns.get("url"))
        ui.link(url, url, new_tab=True) if url else None
        with ui.row(align_items="stretch").classes("w-80 gap-0 items-center text-center"):
            i = ui.input(
                placeholder="URL:", value=url if url else "", validation=lambda v: validate_url(v, data)
            ).props("outlined")
            i.on("blur", lambda x=i: x.validate()).without_auto_validation().classes("w-65")
            del_link = ui.button(icon="delete", on_click=lambda: i.set_value(""))
            del_link.props("text-color=secondary").classes("h-14")
            del_link.on("click", lambda: data.update({columns.get("url"): ""}))
        ui.editor(value=data[columns["comment"]]).bind_value_to(data, columns["comment"])
        md = render_markdown().classes(remove="text-justify")
        md.bind_content_from(data, columns["comment"], backward=lambda x: "" if x is None else x)
        md.bind_visibility(md, "content")
        ui.button("Fertig", icon="check", on_click=lambda: dia.close()).props("text-color=secondary")


def update_row_data(data: dict[str, str], grid: AgGrid, warehouse: Selection):
    grid.run_row_method(data["index"], "setData", data)
    updated = pl.from_dict(data)
    warehouse.inventory = warehouse.inventory.update(updated, on="index", how="full")
