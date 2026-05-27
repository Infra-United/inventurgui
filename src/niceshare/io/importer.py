import duckdb
import polars as pl
from _duckdb import CatalogException, IOException
from polars import DataFrame
from polars.exceptions import NoDataError

from niceshare.helper.config import settings
from niceshare.helper.images import cache_image, match_img_url
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.selection import Selection


def read_inventory(sheet: str) -> Selection:
    inventory = get_path(settings.data_filename)
    try:
        LOGGER.debug(f"Reading sheet {sheet} from {inventory.name}...")
        match inventory.suffix:
            case ".duckdb":
                with duckdb.connect(database=inventory, read_only=True) as con:
                    df = con.query(f"SELECT * FROM {sheet}").pl()
            case ".xlsx":
                df = pl.read_excel(source=inventory, sheet_name=sheet, engine="openpyxl", drop_empty_cols=False)
            case ".ods":
                df = pl.read_ods(source=inventory, sheet_name=sheet, drop_empty_cols=False)
            case ".csv":
                df = pl.read_csv(source=inventory)
            case _:
                LOGGER.warning(f"This file type is not supported: {inventory.name}")
                exit(1)
        return Selection.create(sheet, df)
    except (NoDataError, IOException, CatalogException) as e:
        LOGGER.warning(f"Unable to read {sheet} from {inventory.name}. Full error: {e}", exc_info=True)
        exit(1)


async def handle_images(subfolder: str, df: DataFrame):
    columns = settings.columns
    if "image" in columns and "image" in df.columns:
        for idx, row in enumerate(df.iter_rows(named=True)):
            if row[settings.columns["image"]] is None:
                continue
            if url_dict := match_img_url(row[settings.columns["image"]]):
                df[idx, columns["image"]] = await cache_image(url_dict, subfolder, row[columns["object"]])
    return df
