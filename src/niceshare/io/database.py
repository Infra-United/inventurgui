from typing import Literal

import duckdb
from polars import DataFrame

from niceshare.helper.config import settings
from niceshare.helper.paths import get_path
from niceshare.io.warehouse import Warehouse


class DB:
    Inventory_DB = get_path(f"{settings.data_filename}.duckdb")
    Request_DB = get_path(f"{settings.requests['filename']}.duckdb")

    @classmethod
    def save(cls, name:str, df:DataFrame, db:Literal['inventory', 'request']):
        file = cls.Inventory_DB if db == 'inventory' else cls.Request_DB
        with duckdb.connect(file, read_only=False) as con:
            con.sql(f"DROP TABLE IF EXISTS {name}")
            con.sql(f"CREATE TABLE {name} AS SELECT * FROM df")

    @classmethod
    def load(cls, name:str, db:Literal['inventory', 'request']) -> Warehouse:
        file = cls.Inventory_DB if db == 'inventory' else cls.Request_DB
        with duckdb.connect(database=file, read_only=True) as con:
            df = con.query(f'SELECT * FROM {name}').pl()
            return Warehouse(name, df)
