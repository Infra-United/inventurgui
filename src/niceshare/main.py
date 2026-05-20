import asyncio
import locale
import os

import jwt
from nicegui import ui, app

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.load_data import load_data_from_dav, load_wiki
from niceshare.ui.root import root


# Starts the UI
def main():
    warehouses, pages = asyncio.run(load_data_from_dav())
    if settings.help["wiki"]:
        wiki = asyncio.run(load_wiki())
    else: wiki = None
    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    locale.setlocale(locale.LC_TIME, settings.locale)
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    os.environ.setdefault("NICEGUI_STORAGE_PATH", str(get_path("users")))
    app.add_static_file(local_file=get_path("manifest.json"), url_path="/helpers/manifest.json", strict=False)
    app.add_static_file(local_file=get_path("service_worker.js"), url_path="/helpers/service_worker.js", strict=False)
    app.add_static_file(local_file=get_path("favicon.png"), url_path="/favicon.ico", strict=False)
    app.add_static_files("/splash/", get_path("splash"))
    app.add_static_files("/icons/", get_path("icons"))
    ui.run(
        root=lambda: root(warehouses, pages, wiki),
        language=settings.language,
        uvicorn_logging_level="debug" if ARGS.debug else "info",
        show=False,
        reload=ARGS.reload,
        uvicorn_reload_dirs=str(get_path("").parent.joinpath("src")),
        title=settings.title,
        favicon=get_path(settings.favicon),
        port=settings.port,
        uvicorn_reload_excludes=str(get_path("")),
        storage_secret=storage_secret if storage_secret else "12341232312",
    )
    LOGGER.debug("Successfully started UI.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
