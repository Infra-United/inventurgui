from typing import Any

import polars as pl
from polars.exceptions import NoDataError

from inventurgui.helper.config import settings
from inventurgui.helper.images import cache_image, match_img_url
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


async def read_ods(sheet:str) -> Any | None:
    inventory = get_path(settings.data["path"])
    LOGGER.debug(f"Reading Data from {inventory}...")
    try:
        LOGGER.debug(f"Reading sheet {sheet}...")
        df = pl.read_ods(source=inventory, sheet_name=sheet, drop_empty_cols=False)
        columns = settings.columns
        if columns["image"] in df.columns:
            for idx, row in enumerate(df.iter_rows(named=True)):
                if row[settings.columns["image"]] is None:
                    continue
                if url_dict:=match_img_url(row[settings.columns["image"]]):
                    df[idx, columns["image"]] = await cache_image(url_dict, sheet, row[columns["object"]], thumbnail=True)
        return Warehouse.create(sheet, df)
    except NoDataError:
        LOGGER.warning(f"No data found in sheet {sheet}. Please check if this is intended.")
        return None
