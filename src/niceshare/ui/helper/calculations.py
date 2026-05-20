import polars as pl
from polars import DataFrame

from niceshare.helper.config import settings
from niceshare.io.cache import Cache


async def total_weight(name:str, df:DataFrame) -> int:
    df = await get_final(name, df)
    return df.select(settings.columns["total_weight"]).sum().cast(pl.Int64).item()

async def get_final(name:str, df:DataFrame) -> DataFrame:
    columns = settings.columns
    for row_idx, value in Cache.amounts(name).items():
        df = df.with_columns(
            pl.when(pl.col("index") == int(row_idx))
            .then(pl.lit(value))
            .otherwise(pl.col(columns["count"]))
            .alias(columns["count"]))
    return df.drop("index").with_columns((pl.col(columns["count"]) * pl.col(columns["weight"])).alias(columns["total_weight"]))