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
    def children(self) -> list[str] | None:
        return self.categories

    @override
    @property
    def routes(self) -> dict[str, str]:
        routes: dict[str, str] = {}
        if not self.categories:
            routes.update({self.name: f"/{SELECTION_ROOT}"})
        else:
            for category in self.categories:
                routes.update({category: f"/{SELECTION_ROOT}/{slugify(self.name)}/{slugify(category)}"})
        return routes

    @classmethod
    def create(cls, name: str, df: DataFrame):
        # with pl.Config(tbl_cols=-1):
        #    print(df.filter(pl.col(columns["object"]).str.contains("regal")))
        # selection = cls(name=name, inventory=df.select([c for c in columns.values()]).with_row_index())
        selection = cls(name=name, inventory=df.with_columns(pl.col("index").cast(pl.Int64)))
        print(selection)
        return selection

    @property
    def categories(self) -> list[str] | None:
        try:
            if settings.columns["category"] in self.inventory.columns:
                return sorted(self.inventory[settings.columns["category"]].unique().drop_nulls())
        except (AttributeError, TypeError):
            raise AttributeError(
                "It seems like you have used a category that is not sortable."
                "\nPlease review the categories used in the category column of the inventory file."
                "\nCheck for empty cells, and stuff like numbers, non-ascii-characters, etc."
            )
        return None

    def selected(self) -> DataFrame:
        return self.inventory.filter(pl.col("index").is_in(list(Cache.selected())))