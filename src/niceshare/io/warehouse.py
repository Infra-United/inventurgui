from dataclasses import dataclass
from typing import override

import polars as pl
from polars import DataFrame
from slugify import slugify

from niceshare.helper.config import settings
from niceshare.io.cache import Cache
from niceshare.io.wiki import MenuItem

columns = settings.columns
WAREHOUSE_ROOT = slugify(settings.warehouse["label"])

@dataclass
class Warehouse(MenuItem):
    name: str
    inventory: DataFrame

    @override
    @property
    def children(self) -> list[str]:
        return self.categories

    @override
    @property
    def routes(self) -> dict[str, str]:
        routes: dict[str, str] = {}
        for category in self.categories:
            routes.update({category: f"/{WAREHOUSE_ROOT}/{slugify(self.name)}/{slugify(category)}"})
        return routes

    @classmethod
    def create(cls, name: str, df: DataFrame):
        # with pl.Config(tbl_cols=-1):
        #    print(df.filter(pl.col(columns["object"]).str.contains("regal")))
        df = df.with_columns(
            [
                pl.col(columns["count"]).cast(pl.Int64, strict=False),
                pl.col(columns["weight"]).cast(pl.Float64, strict=False),
                pl.col(columns["count"]).alias(columns["total"]).cast(pl.Int64, strict=False),
            ]
        )
        df.insert_column(1, (pl.col(columns["count"]) * pl.col(columns["weight"])).alias(columns["total_weight"]))
        warehouse = cls(name=name, inventory=df.select([c for c in columns.values()]).with_row_index())
        warehouse.inventory.insert_column(0, (pl.lit(name)).alias(settings.warehouse["label"]))
        return warehouse

    @property
    def categories(self) -> list[str]:
        try:
            c: list[str] = sorted(self.inventory[settings.columns["category"]].unique())
            if len(c) == 1:
                c[0] = self.name
            else:
                c.insert(1, self.name)
        except (AttributeError, TypeError):
            raise AttributeError(
                "It seems like you have used a category that is not sortable."
                "\nPlease review the categories used in the category column of the inventory file."
                "\nCheck for empty cells, and stuff like numbers, non-ascii-characters, etc."
            )
        c.insert(0, settings.warehouse["selection"])
        return c

    def selected(self) -> DataFrame:
        return self.inventory.filter(pl.arange(0, self.inventory.height).is_in(Cache.selected(self.name)))
