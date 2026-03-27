from io import BytesIO
from pathlib import Path

import httpx
import nicegui.run
from PIL import Image, UnidentifiedImageError
from nicegui import app
from nicegui.events import UploadEventArguments
from slugify import slugify

from inventurgui.cli import ARGS
from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.ui.helper.validators import IMG_URL_REGEX


def make_thumbnail(path: Path):
    if path.is_file():
        image = Image.open(path)
        image.thumbnail((600, 600))
        image.save(path)

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

async def cache_image(src: str, subfolder:str, filename: str, thumbnail:bool = False):
    url_dict: dict|None = match_img_url(src)
    if url_dict and url_dict["domain"] != settings.domain:
        path = construct_img_path(subfolder, filename, url_dict.get("ext"))
        if not path.is_file() and not ARGS.dev: # Guard clause for dev environment to download images only once
            try:
                response = await nicegui.run.io_bound(httpx.get,url_dict["url"], timeout=5)
                if response.status_code == 200 and response.headers["content-type"].startswith("image"):
                    image = Image.open(BytesIO(response.content))
                    image.save(path)
                    if thumbnail:
                        make_thumbnail(path)
                    LOGGER.info(f"Successfully downloaded image from {url_dict['url']} and saved to {path}")
            except httpx.TimeoutException, UnidentifiedImageError, ValueError, OSError:
                LOGGER.exception(f"Could not download image from {url_dict['url']} and save it to {path}", exc_info=True)
                return None
        img_url = construct_img_url(subfolder, filename, url_dict.get("ext"), domain=False)
        app.add_static_file(local_file=path, url_path=img_url)
        return construct_img_url(subfolder, filename, url_dict.get("ext"), domain=True)
    else: # No img URL found in src
        LOGGER.debug(f"Could not download image in {src}")
        return None
