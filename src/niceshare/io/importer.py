import polars as pl
from polars import DataFrame
from polars.exceptions import NoDataError

from niceshare.helper.config import settings
from niceshare.helper.images import cache_image, match_img_url
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.warehouse import Warehouse


def read_ods(sheet:str) -> Warehouse:
    inventory = get_path(f"{settings.data_filename}.ods")
    LOGGER.debug(f"Reading Data from {inventory}...")
    try:
        LOGGER.debug(f"Reading sheet {sheet}...")
        df = pl.read_ods(source=inventory, sheet_name=sheet, drop_empty_cols=False)
        return Warehouse.create(sheet, df)
    except NoDataError:
        LOGGER.warning(f"No data found in sheet {sheet}. Please check if this is intended.")
        exit(1)

async def handle_images(subfolder:str, df:DataFrame):
    columns = settings.columns
    if "image" in columns and "image" in df.columns:
        for idx, row in enumerate(df.iter_rows(named=True)):
            if row[settings.columns["image"]] is None:
                continue
            if url_dict := match_img_url(row[settings.columns["image"]]):
                df[idx, columns["image"]] = await cache_image(url_dict, subfolder, row[columns["object"]])
    return df