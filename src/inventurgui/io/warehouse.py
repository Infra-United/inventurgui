from typing import Generator

import polars as pl
from nicegui.elements.aggrid import AgGrid
from polars import DataFrame, Series

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache

columns = settings.columns

class Warehouse:
    _grid: AgGrid = None

    def __init__(self, name: str, df: DataFrame):
        self.name = name
        self.inventory = df.with_columns([pl.col(columns["count"]).cast(pl.Int8, strict=False),
                                          pl.col(columns["weight"]).cast(pl.Int8, strict=False),
                                          pl.col(columns["count"] * 1).alias(i18n.get("cart.of")),
                                          pl.lit(self.name).alias(settings.warehouse["label"])],
                                         )
        # Move warehouse column to first place
        cols = self.inventory.columns
        new_order = [cols[-1]] + cols[:-1]
        self.inventory = self.inventory.select(new_order)

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

    @property
    def count(self) -> int:
        return self.inventory.height

    def selected(self) -> DataFrame:
        return self.inventory.filter(pl.arange(0, self.count).is_in(Cache.selected(self.name)))

    def get_final(self) -> DataFrame | None:
        changed_amounts = {int(k): v for k, v in Cache.amounts(self.name).items()}
        df = self.inventory.filter(pl.arange(0, self.count).is_in(changed_amounts)).select(columns["count"])
        if df.is_empty():
            return None
        print(df)
        # For each row_id and associated values
        """for row_id, values in user_amounts.items():
            # Create a boolean mask where 'perma_id' matches row_id
            mask = df.row(by_predicate=(pl.col('index') == row_id))
            # Update the target column for all matching rows
            df.loc[mask, columns["count"]] = int(values[0])
        return df.drop("index", strict=False)
"""