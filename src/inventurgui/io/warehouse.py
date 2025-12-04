from nicegui.elements.aggrid import AgGrid
from pandas import DataFrame

from inventurgui.helper.config import config

class Warehouse:
    _grid: AgGrid = None
    def __init__(self, name:str, inventory:DataFrame):
        self.name = name
        self.inventory = inventory
        self.inventory.insert(0, 'perma_id', self.inventory.index.tolist()) # This ensures we can have selection across grids

    @property
    def categories(self) -> list[str]:
        c:list[str] = sorted(self.inventory[config['data']['category']].unique())
        return c
