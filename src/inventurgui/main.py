import asyncio
import os
from typing import Tuple

import ezodf
import jwt
import polars as pl
from nicegui import ui, app
from polars.exceptions import NoDataError

from inventurgui.cli import ARGS
from inventurgui.helper.config import settings, create_default_config
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path, ensure_dirs
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.helper.markdown import get_markdown
from inventurgui.ui.root import root


# Helper function to make sure everything is set up correctly on startup
async def backend() -> Tuple[list[Warehouse], dict[str, str]] :
    #nc = Nextcloud.singleton()
    #for key, file in settings.cloud["pull"].items():
        #await nc.pull_file(key, file)
    # Read Inventory File
    warehouses = []
    inventory = get_path(settings.data["path"])
    LOGGER.debug(f"Reading Data from {inventory}...")
    for sheet_num, sheet in enumerate(ezodf.opendoc(inventory).sheets):
        if sheet_num >= settings.data["sheets"]:
            continue
        try:
            LOGGER.debug(f"Reading sheet {sheet.name}...")
            df = pl.read_ods(source=inventory, sheet_name=sheet.name, drop_empty_cols=False)
            warehouses.append(Warehouse(name=sheet.name, df=df))
        except NoDataError:
            LOGGER.warning(f"No data found in sheet {sheet.name}. Please check if this is intended.")
    # Create default config
    create_default_config()
    # Ensure Filesystem Structure
    ensure_dirs([w.name for w in warehouses])
    # Read .md files
    markdown = get_markdown()
    # Manage env vars
    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    return warehouses, markdown

# Starts the UI
def frontend(warehouses:list[Warehouse], markdown:dict[str, str]):
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    os.environ.setdefault("NICEGUI_STORAGE_PATH", str(get_path("users")))
    app.add_static_files('/images', str(get_path("images")))
    ui.run(
        root=lambda: root(warehouses, markdown),
        language=settings.language,
        uvicorn_logging_level="debug" if ARGS.debug else "info",
        show=False,
        reload=ARGS.reload,
        uvicorn_reload_dirs=str(get_path("").parent.joinpath("src")),
        title=settings.title,
        favicon=get_path(settings.favicon),
        port=settings.port,
        storage_secret=storage_secret if storage_secret else '12341232312',
    )
    LOGGER.debug("Successfully started UI.")

if __name__ in {"__main__", "__mp_main__"}:
    whs, mds = asyncio.run(backend())
    frontend(whs, mds)