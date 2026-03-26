from pathlib import Path

from nicegui import app
from nicegui.elements.aggrid import AgGrid
from nicegui.events import UploadEventArguments
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


def get_img_url(warehouse_name: str, filename: str, file_extension:str, domain: bool) -> str:
    if domain:
        return f"{settings.domain}/images/{slugify(warehouse_name)}/{slugify(filename)}.{file_extension}"
    else:
        return f"/images/{slugify(warehouse_name)}/{slugify(filename)}.{file_extension}"


def get_img_path(warehouse_name: str, filename: str, file_extension:str) -> Path:
    return get_path(f"{slugify(warehouse_name)}/{slugify(filename)}.{file_extension}", "images")


async def upload_img(warehouse:Warehouse, event: UploadEventArguments, data:dict, grid:AgGrid):
    file_extension = event.file.name.split(".")[-1]
    filename = data[settings.columns['object']]
    path = get_img_path(warehouse.name, filename , file_extension)
    path.unlink(missing_ok=True)
    await event.file.save(path)
    img_url = get_img_url(warehouse.name, filename, file_extension, domain=False)
    app.add_static_file(local_file=path, url_path=img_url)
    data[settings.columns["image"]] = get_img_url(warehouse.name, filename,file_extension, domain=True)
    await grid.run_row_method(data.get("index"), "setData", data)
    warehouse.inventory[data.get("index"), settings.columns["image"]] = data[settings.columns["image"]]

async def delete_img(img_url: str, data: dict, grid:AgGrid ,warehouse:Warehouse):
    split = img_url.split("/")
    if split[0] == settings.domain:
        get_path("/".join(split[-2:-1]), "images").unlink()
        app.remove_route(img_url)
    data[settings.columns["image"]] = ""
    await grid.run_row_method(data.get("index"), "setData", data)
    warehouse.inventory[data.get("index"), settings.columns["image"]] = ""
