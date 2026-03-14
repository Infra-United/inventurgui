import ezodf
import polars as pl
from polars.exceptions import NoDataError

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


def read_inventory() -> list[Warehouse]:
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
    return warehouses