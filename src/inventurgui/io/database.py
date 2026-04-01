import duckdb
from polars import DataFrame

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse


class DB:
    DB_FILE = get_path(f"{settings.data_filename}.duckdb")

    @classmethod
    def save(cls, name:str, df:DataFrame):
        with duckdb.connect(cls.DB_FILE, read_only=False) as con:
            con.sql(f"DROP TABLE IF EXISTS {name}")
            con.sql(f"CREATE TABLE {name} AS SELECT * FROM df")


    @classmethod
    def load(cls, name:str) -> Warehouse:
        with duckdb.connect(database=cls.DB_FILE, read_only=True) as con:
            df = con.query(f'SELECT * FROM {name}').pl()
            return Warehouse(name, df)
