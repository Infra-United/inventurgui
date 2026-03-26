from pathlib import Path
from typing import Tuple

from nicegui import app
from nicegui.elements.aggrid import AgGrid
from nicegui.events import UploadEventArguments
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


def get_img_url(subfolder: str, filename: str, file_extension:str, domain: bool) -> str:
    if domain:
        return f"{settings.domain}/images/{slugify(subfolder)}/{slugify(filename)}.{file_extension}"
    else:
        return f"/images/{slugify(subfolder)}/{slugify(filename)}.{file_extension}"


def get_img_path(subfolder: str, filename: str, file_extension:str) -> Path:
    return get_path(f"{slugify(subfolder)}/{slugify(filename)}.{file_extension}", "images")

def get_img_parts_from_url(img_url: str) -> Tuple[str, str, str, str]:
    split = img_url.split("/")
    domain = split[0]
    subfolder = split[-2]
    filename = split[-1].split(".")[0]
    extension = split[-1].split(".")[-1]
    return domain, subfolder, filename, extension


async def upload_img(warehouse:Warehouse, event: UploadEventArguments, data:dict, grid:AgGrid):
    file_extension = event.file.name.split(".")[-1]
    filename = data[settings.columns['object']]
    path = get_img_path(warehouse.name, filename , file_extension)
    await delete_img(data, grid, warehouse)
    await event.file.save(path)
    img_url = get_img_url(warehouse.name, filename, file_extension, domain=False)
    app.add_static_file(local_file=path, url_path=img_url)
    data[settings.columns["image"]] = get_img_url(warehouse.name, filename,file_extension, domain=True)
    await grid.run_row_method(data.get("index"), "setData", data)
    warehouse.inventory[data.get("index"), settings.columns["image"]] = data[settings.columns["image"]]

async def delete_img(data: dict, grid:AgGrid, warehouse:Warehouse):
    domain, subfolder, filename, extension = get_img_parts_from_url(data[settings.columns["image"]])
    if domain == settings.domain:
        get_img_path(subfolder, filename, extension).unlink()
        app.remove_route(get_img_url(subfolder, filename, extension, domain=False))
    data[settings.columns["image"]] = ""
    await grid.run_row_method(data.get("index"), "setData", data)
    warehouse.inventory[data.get("index"), settings.columns["image"]] = ""
