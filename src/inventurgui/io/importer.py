from typing import Generator

import polars as pl
from polars.exceptions import NoDataError

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


def read_inventory() -> Generator[Warehouse, None, None]:
    inventory = get_path(settings.data["path"])
    LOGGER.debug(f"Reading Data from {inventory}...")
    for name in settings.data["warehouses"]:
        try:
            LOGGER.debug(f"Reading sheet {name}...")
            df = pl.read_ods(source=inventory, sheet_name=name, drop_empty_cols=False)
            yield Warehouse.create(name, df)
        except NoDataError:
            LOGGER.warning(f"No data found in sheet {name}. Please check if this is intended.")

