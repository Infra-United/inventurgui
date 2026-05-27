from typing import Tuple

from _duckdb import IOException, CatalogException

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import ensure_directory_structure
from niceshare.io.database import DB
from niceshare.io.importer import read_inventory, handle_images
from niceshare.io.nextcloud import Nextcloud
from niceshare.io.warehouse import Warehouse
from niceshare.io.wiki import Wiki, read_wiki, pull_wiki
from niceshare.ui.helper.markdown import read_page_files


async def load_data_from_dav(reload: bool = False) -> Tuple[list[Warehouse], dict[str, str]]:
    if not ARGS.reload or reload:
        Nextcloud.singleton().pull_files()
    warehouses: list[Warehouse] = []
    for sheet in settings.data["warehouses"]:
        try:
            warehouse: Warehouse = DB.load(sheet, "inventory")
        except IOException, CatalogException:
            LOGGER.warning(f"Could not load {sheet} from database. Trying to import it.")
            warehouse: Warehouse = read_inventory(sheet)
            DB.save(warehouse.name, warehouse.inventory, "inventory")
        warehouses.append(warehouse)
    [await handle_images(w.name, w.inventory) for w in warehouses]
    ensure_directory_structure([w.name for w in warehouses])
    pages: dict[str, str] = {k: v for k, v in read_page_files()}
    return warehouses, pages


async def load_wiki(reload: bool = False) -> Wiki:
    if not ARGS.reload or reload:
        await pull_wiki()
    return await read_wiki()
