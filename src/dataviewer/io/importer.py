import polars as pl
from polars import DataFrame
from polars.exceptions import NoDataError

from dataviewer.helper.config import settings
from dataviewer.helper.images import cache_image, match_img_url
from dataviewer.helper.logger import LOGGER
from dataviewer.helper.paths import get_path
from dataviewer.io.selection import Selection


def read_ods(sheet: str) -> Selection:
    inventory = get_path(f"{settings.data_filename}.csv")
    LOGGER.debug(f"Reading Data from {inventory}...")
    try:
        LOGGER.debug(f"Reading sheet {sheet}...")
        df = pl.read_csv(source=inventory, encoding="utf-8")
        LOGGER.info(f"Successfully read sheet {sheet}.")
        return Selection.create(sheet, df)
    except NoDataError:
        LOGGER.warning(f"No data found in sheet {sheet}. Please check if this is intended.")
        exit(1)


async def handle_images(subfolder: str, df: DataFrame):
    columns = settings.columns
    if columns["image"] in df.columns:
        for idx, row in enumerate(df.iter_rows(named=True)):
            if row[settings.columns["image"]] is None:
                continue
            if url_dict := match_img_url(row[settings.columns["image"]]):
                df[idx, columns["image"]] = await cache_image(url_dict, subfolder, row[columns["object"]])
    return df
