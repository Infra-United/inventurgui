from typing import Tuple

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import ensure_directory_structure
from niceshare.io.database import DB
from niceshare.io.importer import read_ods, handle_images
from niceshare.io.nextcloud import Nextcloud
from niceshare.io.warehouse import Warehouse
from niceshare.io.wiki import Wiki, read_wiki, pull_wiki
from niceshare.ui.helper.markdown import read_page_files


async def load_data_from_dav(reload:bool=False) -> Tuple[list[Warehouse], dict[str, str]]:
    if not ARGS.reload or reload:
        Nextcloud.singleton().pull_files()
    if DB.Inventory_DB.is_file() and not reload and not ARGS.reload:
        warehouses: list[Warehouse] = [DB.load(sheet, 'inventory') for sheet in settings.data["warehouses"]]
        LOGGER.info("Found inventory DB and loaded data.")
    else:
        warehouses: list[Warehouse] = [read_ods(sheet) for sheet in settings.data["warehouses"]]
        [DB.save(w.name, w.inventory, 'inventory') for w in warehouses]
        LOGGER.info("Created inventory DB and loaded data.")
    [await handle_images(w.name, w.inventory) for w in warehouses]
    ensure_directory_structure([w.name for w in warehouses])
    pages: dict[str, str] = {k: v for k, v in read_page_files()}
    return warehouses, pages

async def load_wiki(reload:bool=False) -> Wiki:
    if not ARGS.reload or reload:
        await pull_wiki()
    return await read_wiki()