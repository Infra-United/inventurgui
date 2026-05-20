import base64
from contextlib import suppress
from io import BytesIO
from os import mkdir
from pathlib import Path

import httpx
import qrcode
from PIL import Image, UnidentifiedImageError
from nicegui import app, nicegui, ui
from nicegui.events import UploadEventArguments
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from slugify import slugify
from starlette.requests import ClientDisconnect

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.ui.helper.validators import IMG_URL_REGEX


def make_thumbnail(path: Path, size: int = 600):
    if path.is_file():
        image = Image.open(path)
        image.thumbnail((size, size))
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
    try:
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
        ui.notify(f"Upload successful.")
    except ClientDisconnect:
        ui.notify("Connection failed, please retry uploading the image.")

async def delete_img(data: dict):
    url_dict: dict|None = match_img_url(data[settings.columns["image"]])
    if url_dict and url_dict.get("domain") == settings.domain:
        with suppress(FileNotFoundError):
            get_path(url_dict["path"]).unlink(missing_ok=True)
            app.remove_route(url_dict.get("path"))
            ui.notify(f"Deleted {url_dict["path"]}")
    data[settings.columns["image"]] = ""

async def cache_image(url_dict: dict[str, str], subfolder:str, filename: str, thumbnail_size:int = 600):
    path = construct_img_path(subfolder, filename, url_dict["ext"])
    if not path.is_file() and url_dict["domain"] != settings.domain or ARGS.images:
        try:
            response = await nicegui.run.io_bound(httpx.get,url_dict["url"], timeout=5)
            if response.status_code == 200 and response.headers["content-type"].startswith("image"):
                image = Image.open(BytesIO(response.content))
                if not get_path(subfolder, "images").is_dir():
                    mkdir(get_path(subfolder, "images"))
                image.save(path)
                make_thumbnail(path, thumbnail_size)
                LOGGER.info(f"Successfully downloaded image from {url_dict['url']} and saved to {path}")
        except httpx.TimeoutException, httpx.ReadTimeout, UnidentifiedImageError, ValueError, OSError:
            LOGGER.exception(f"Could not download image from {url_dict['url']} and save it to {path}", exc_info=True)
            return None
    img_url = construct_img_url(subfolder, filename, url_dict["ext"], domain=False)
    try:
        app.add_static_file(local_file=path, url_path=img_url)
    except FileNotFoundError:
        return url_dict.get("url")
    return construct_img_url(subfolder, filename, url_dict["ext"], domain=True)

async def cache_base64_img(src:str, subfolder:str, filename:str, thumbnail_size:int = 600):
    split = src.split(";base64,")
    base = split[-1]
    ext = split[0].split("/")[-1]
    path = construct_img_path(subfolder, filename, ext)
    if not path.is_file() or ARGS.images:
        try:
            Image.open(BytesIO(base64.b64decode(base))).save(path)
            make_thumbnail(path, thumbnail_size)
            LOGGER.info(f"Successfully converted image from {split[-1]} and saved to {path}.")
        except IOError:
            LOGGER.exception(f"Could not convert image from {split[-1]} and save it to {path}", exc_info=True)
            return src
    img_url = construct_img_url(subfolder, filename, ext, domain=False)
    try:
        app.add_static_file(local_file=path, url_path=img_url)
    except FileNotFoundError:
        return src
    return construct_img_url(subfolder, filename, ext, domain=True)

def generate_qrcode(data: str, subfolder:str, filename:str):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(), embedded_image_path=get_path(settings.logo))
    path = construct_img_path(subfolder, filename, "png")
    img.save(path)
    return img, path