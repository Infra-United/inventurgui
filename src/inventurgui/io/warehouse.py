from typing import Generator

import pandas as pd
from nicegui.elements.aggrid import AgGrid
from pandas import DataFrame, Series

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache

columns = settings.columns

class Warehouse:
    _grid: AgGrid = None

    def __init__(self, name: str, inventory: DataFrame):
        self.name = name
        inventory[columns["count"]] = pd.to_numeric(inventory[columns["count"]], 'coerce', downcast='integer')
        inventory[columns["weight"]] = pd.to_numeric(inventory[columns["weight"]], 'coerce', downcast='integer')
        self.inventory = inventory
        self.inventory.insert(
            0, "perma_id", self.inventory.index.tolist()
        )  # This ensures we can have selection across grids
        total_loc = self.inventory.columns.get_loc(columns["count"])+1
        self.inventory.insert(total_loc, i18n.get("cart.of"), inventory[columns["count"]])
        self.inventory.insert(0, settings.warehouse["label"], self.name)

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
        return self.inventory.index.max()

    def selected(self) -> DataFrame:
        row_ids: list = list(Cache.selected(self.name))
        def _match_selected() -> Generator[Series, None, None]:
            for row_id in row_ids:
                for df_id, row_data in self.inventory.iterrows():
                    if str(df_id) == row_id:
                        yield row_data

        return DataFrame.from_records([r for r in _match_selected()])

    def get_final(self) -> DataFrame | None:
        df = self.selected()
        if df is None or df.empty:
            return None
        user_amounts = Cache.amounts().get(self.name, {})
        # For each row_id and associated values
        for row_id, values in user_amounts.items():
            # Create a boolean mask where 'perma_id' matches row_id
            mask = df.get("perma_id") == int(row_id)
            # Update the target column for all matching rows
            df.loc[mask, columns["count"]] = int(values[0])
        df.drop("perma_id", axis=1, inplace=True)
        return df
