import duckdb
from polars import DataFrame

from dataviewer.helper.config import settings
from dataviewer.helper.paths import get_path
from dataviewer.io.selection import Selection


class DB:
    DB_FILE = get_path(f"{settings.data_filename}.duckdb")

    @classmethod
    def save(cls, name: str, df: DataFrame):
        with duckdb.connect(cls.DB_FILE, read_only=False) as con:
            con.sql(f"DROP TABLE IF EXISTS {name}")
            con.sql(f"CREATE TABLE {name} AS SELECT * FROM df")

    @classmethod
    def load(cls, name: str) -> Selection:
        with duckdb.connect(database=cls.DB_FILE, read_only=True) as con:
            df = con.query(f"SELECT * FROM {name}").pl()
            return Selection(name, df)
