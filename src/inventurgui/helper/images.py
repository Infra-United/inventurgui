from io import BytesIO
from os import mkdir
from pathlib import Path

import httpx
from PIL import Image, UnidentifiedImageError
from nicegui import app, nicegui
from nicegui.events import UploadEventArguments
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.ui.helper.validators import IMG_URL_REGEX


def make_thumbnail(path: Path):
    if path.is_file():
        image = Image.open(path)
        image.thumbnail((600, 600))
        image.save(path)

def compress_image(path:Path):
    image = Image.open(path)
    if image.format not in {".jpg", ".jpeg", ".png"}:
        image.save(path)
    # Save back to the same path, overwriting the original file
    if image.format in {".jpg", ".jpeg"}:
        image.save(path, quality=80, optimize=True)
    else:
        image.save(path, optimize=True, compress_level=9)

def match_img_url(to_test: str) -> dict | None:
    try:
        return IMG_URL_REGEX.search(to_test).groupdict()
    except AttributeError:
        return None

def construct_img_url(subfolder: str, filename: str, file_extension:str, domain: bool) -> str:
    if domain:
        return f"{settings.domain}/images/{slugify(subfolder)}/{slugify(filename)}.{file_extension}"
    else:
        return f"/images/{slugify(subfolder)}/{slugify(filename)}.{file_extension}"


def construct_img_path(subfolder: str, filename: str, file_extension: str) -> Path:
    return get_path(f"{slugify(subfolder)}/{slugify(filename)}.{file_extension}", "images")

async def upload_img(warehouse_name:str, event: UploadEventArguments, data:dict):
    file_extension = event.file.name.split(".")[-1]
    filename = data[settings.columns['object']]
    path = construct_img_path(warehouse_name, filename, file_extension)
    img_url = construct_img_url(warehouse_name, filename, file_extension, domain=False)
    path.unlink(missing_ok=True)
    app.remove_route(img_url)
    await event.file.save(path)
    make_thumbnail(path)
    app.add_static_file(local_file=path, url_path=img_url)
    data[settings.columns["image"]] = construct_img_url(warehouse_name, filename, file_extension, domain=True)

async def delete_img(data: dict):
    url_dict: dict|None = match_img_url(data[settings.columns["image"]])
    if url_dict and url_dict.get("domain") == settings.domain:
        get_path(url_dict.get("path")).unlink()
        app.remove_route(url_dict.get("path"))
    data[settings.columns["image"]] = ""

async def cache_image(url_dict: dict, subfolder:str, filename: str, thumbnail:bool = False, compress:bool = False):
    path = construct_img_path(subfolder, filename, url_dict.get("ext"))
    if not path.is_file() and url_dict["domain"] != settings.domain: # Guard clause for dev environment to download images only once
        try:
            response = await nicegui.run.io_bound(httpx.get,url_dict["url"], timeout=5)
            if response.status_code == 200 and response.headers["content-type"].startswith("image"):
                image = Image.open(BytesIO(response.content))
                if not get_path(subfolder, "images").is_dir():
                    mkdir(get_path(subfolder, "images"))
                image.save(path)
                if compress:
                    compress_image(path)
                elif thumbnail:
                    make_thumbnail(path)
                LOGGER.info(f"Successfully downloaded image from {url_dict['url']} and saved to {path}")
        except httpx.TimeoutException, httpx.ReadTimeout, UnidentifiedImageError, ValueError, OSError:
            LOGGER.exception(f"Could not download image from {url_dict['url']} and save it to {path}", exc_info=True)
            return None
    img_url = construct_img_url(subfolder, filename, url_dict.get("ext"), domain=False)
    try:
        app.add_static_file(local_file=path, url_path=img_url)
    except FileNotFoundError:
        return url_dict.get("url")
    return construct_img_url(subfolder, filename, url_dict.get("ext"), domain=True)
