from typing import Literal

import duckdb
from polars import DataFrame

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


class DB:
    Inventory_DB = get_path(f"{settings.data_filename}.duckdb")
    Request_DB = get_path(f"{settings.requests['filename']}.duckdb")

    @classmethod
    def save(cls, name:str, df:DataFrame, db:Literal['inventory', 'request']):
        with duckdb.connect(cls.Inventory_DB, read_only=False) as con:
            con.sql(f"DROP TABLE IF EXISTS {name}")
            con.sql(f"CREATE TABLE {name} AS SELECT * FROM df")


    @classmethod
    def load(cls, name:str, db:Literal['inventory', 'request']) -> Warehouse:
        with duckdb.connect(database=cls.Inventory_DB, read_only=True) as con:
            df = con.query(f'SELECT * FROM {name}').pl()
            return Warehouse(name, df)
