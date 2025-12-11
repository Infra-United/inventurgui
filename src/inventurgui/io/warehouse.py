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
        self.inventory.insert(0, 'warehouse', self.name)

    @property
    def categories(self) -> list[str]:
        c:list[str] = sorted(self.inventory[config['data']['category']].unique())
        c.insert(0, config['everything'])
        return c

    @property
    async def selected(self) -> DataFrame | None:
        row_ids: list = list(app.storage.user.get(self.name))
        return await run.cpu_bound(_get_selected, self.inventory.iterrows, row_ids)


def _get_selected(iterator:Any, row_ids:list[str]) -> DataFrame:
    def _match_selected() -> Generator[Series, None, None]:
        for row_id in row_ids:
            for i, row_data in iterator():
                if str(i) == row_id:
                    yield row_data
    return DataFrame.from_records([r for r in _match_selected()])