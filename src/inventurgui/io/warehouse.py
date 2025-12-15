from collections.abc import ItemsView
from typing import Generator, Any

from nicegui import app, run
from nicegui.elements.aggrid import AgGrid
from pandas import DataFrame, Series

from inventurgui.helper.config import config


class Warehouse:
    _grid: AgGrid = None
    def __init__(self, name:str, inventory:DataFrame):
        self.name = name
        self.inventory = inventory
        self.inventory.insert(0, 'perma_id', self.inventory.index.tolist()) # This ensures we can have selection across grids
        self.inventory.insert(0, config['menu']['warehouse']['label'], self.name)

    @property
    def categories(self) -> list[str]:
        c:list[str] = sorted(self.inventory[config['data']['category']].unique())
        c.insert(0, config['everything'])
        return c

    async def selected(self) -> DataFrame | None:
        row_ids: list = list(app.storage.user.get(self.name))
        return await run.cpu_bound(_get_selected, self.inventory.iterrows, row_ids)

    async def get_final(self) -> DataFrame | None:
        df = await self.selected()
        if df is None or df.empty:
            return None
        user_amounts = app.storage.user['amounts'].get(self.name, {})
        # For each row_id and associated values
        for row_id, values in user_amounts.items():
            # Create a boolean mask where 'perma_id' matches row_id
            mask = df.get('perma_id') == int(row_id)
            # Update the target column for all matching rows
            df.loc[mask, config['data']['count']] = int(values[0])
        df.drop('perma_id', axis=1, inplace=True)
        return df

def _get_selected(iterator:Any, row_ids:list[str]) -> DataFrame:
    def _match_selected() -> Generator[Series, None, None]:
        for row_id in row_ids:
            for df_id, row_data in iterator():
                if str(df_id) == row_id:
                    yield row_data
    return DataFrame.from_records([r for r in _match_selected()])