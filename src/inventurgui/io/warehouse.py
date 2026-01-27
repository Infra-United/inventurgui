from typing import Generator, Any

import pandas as pd
from nicegui import app, run
from nicegui.elements.aggrid import AgGrid
from pandas import DataFrame, Series

from inventurgui.helper.config import load_config


class Warehouse:
    _grid: AgGrid = None

    def __init__(self, name: str, inventory: DataFrame):
        self.name = name
        data = load_config()['data']
        inventory[data["count"]] = pd.to_numeric(inventory[data["count"]], 'coerce', downcast='integer')
        inventory[data["weight"]] = pd.to_numeric(inventory[data["weight"]], 'coerce', downcast='integer')
        self.inventory = inventory
        self.inventory.insert(
            0, "perma_id", self.inventory.index.tolist()
        )  # This ensures we can have selection across grids
        self.inventory.insert(0, "total", inventory[data["count"]])
        self.inventory.insert(0, load_config()["warehouse"]["label"], self.name)

    @property
    def categories(self) -> list[str]:
        warehouse_conf: dict = load_config()["warehouse"]
        try:
            c: list[str] = sorted(self.inventory[load_config()["data"]["category"]].unique())
        except (AttributeError, TypeError):
            raise AttributeError("It seems like you have used a category that is not sortable."
                             "\nPlease review the categories used in the category column of the inventory file."
                             "\nCheck for empty cells, and stuff like numbers, non-ascii-characters, etc.")
        c.insert(0, warehouse_conf["selection"])
        c.insert(1, warehouse_conf["everything"])
        return c

    def selected(self) -> DataFrame:
        row_ids: list = list(app.storage.user.get(self.name))
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
        user_amounts = app.storage.user["amounts"].get(self.name, {})
        # For each row_id and associated values
        for row_id, values in user_amounts.items():
            # Create a boolean mask where 'perma_id' matches row_id
            mask = df.get("perma_id") == int(row_id)
            # Update the target column for all matching rows
            df.loc[mask, load_config()["data"]["count"]] = int(values[0])
        df.drop("perma_id", axis=1, inplace=True)
        return df