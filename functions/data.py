 # read ods file to get inventory data
from logging import debug
from pandas import DataFrame
from pandas_ods_reader import read_ods

def get_ods_data(path) -> DataFrame:    
    debug(f"Reading Data from {path}...")
    return read_ods(path)