from dataclasses import dataclass
from typing import override

import polars as pl
from polars import DataFrame
from slugify import slugify

from niceshare.helper.config import settings
from niceshare.io.cache import Cache

columns = settings.columns
SELECTION_ROOT = slugify(settings.selection["label"])


@dataclass
class Selection:
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
            routes.update({category: f"/{SELECTION_ROOT}/{slugify(self.name)}/{slugify(category)}"})
        return routes

    @classmethod
    def create(cls, name: str, df: DataFrame):
        # with pl.Config(tbl_cols=-1):
        #    print(df.filter(pl.col(columns["object"]).str.contains("regal")))
        # selection = cls(name=name, inventory=df.select([c for c in columns.values()]).with_row_index())
        selection = cls(name=name, inventory=df.with_row_index())
        selection.inventory.insert_column(0, (pl.lit(name)).alias(settings.selection["label"]))
        print(selection)
        return selection

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
        c.insert(0, settings.selection["selection"])
        return c

    def selected(self) -> DataFrame:
        return self.inventory.filter(pl.arange(0, self.inventory.height).is_in(Cache.selected(self.name)))

    async def get_final(self) -> DataFrame:
        df = self.inventory
        for row_idx, value in Cache.amounts(self.name).items():
            df[int(row_idx), columns["count"]] = value
        return df.filter(pl.arange(0, self.inventory.height).is_in(Cache.selected(self.name))).drop("index")
