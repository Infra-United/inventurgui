from typing import NamedTuple

import polars as pl
from polars import DataFrame

from inventurgui.helper.config import settings
from inventurgui.io.cache import Cache

columns = settings.columns

class Warehouse(NamedTuple):
    name :str
    inventory : DataFrame

    @classmethod
    def create(cls, name: str, df: DataFrame):
        df = df.with_columns([pl.col(columns["count"]).cast(pl.Int32, strict=False),
                              pl.col(columns["category"]).cast(pl.Categorical, strict=False),
                              pl.col(columns["shelf"]).cast(pl.Categorical, strict=False),
                              pl.col(columns["weight"]).cast(pl.Float32, strict=False),
                              pl.col(columns["count"]).alias(columns["total"]).cast(pl.Int32, strict=False),
                              ])
        df.insert_column(1, (pl.col(columns['count']) * pl.col(columns['weight'])).alias(columns["total_weight"]))
        df = df.select([c for c in columns.values()])
        df.insert_column(0, (pl.arange(0, df.height)).alias("perma_id"))
        with pl.Config(tbl_cols=-1):
            print(df)
        return cls(name=name, inventory=df)

    @property
    def categories(self) -> list[str]:
        try:
            c: list[str] = sorted(self.inventory[settings.columns["category"]].unique())
        except (AttributeError, TypeError):
            raise AttributeError("It seems like you have used a category that is not sortable."
                             "\nPlease review the categories used in the category column of the inventory file."
                             "\nCheck for empty cells, and stuff like numbers, non-ascii-characters, etc.")
        c.insert(0, settings.warehouse["selection"])
        c.insert(1, settings.warehouse["everything"])
        return c

    def selected(self) -> DataFrame:
        return self.inventory.filter(pl.arange(0, self.inventory.height).is_in(Cache.selected(self.name)))

    async def get_final(self) -> DataFrame | None:
        df = self.selected()
        if df.is_empty():
            return None
        changed_amounts = {int(k): v for k, v in Cache.amounts(self.name).items()}
        update_df = self.inventory.filter(pl.arange(0, self.inventory.height).is_in(changed_amounts))
        if not update_df.is_empty():
            df.update(update_df)
        return df.drop('perma_id')