import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

import pandas as pd
from ezodf import opendoc, Sheet, newdoc, Cell
from ezodf.document import FlatXMLDocument, PackagedDocument
from pandas import DataFrame

from inventurgui.helper.config import config, get_path, request_conf
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse


async def write_ods(request: dict[str, str], warehouses: list[Warehouse]) -> None:
    path = get_path(config['cloud']['push']['requests'])
    LOGGER.info(f"Writing to file {path}")

    # Get or create doc and overview_sheet
    ods, overview_sheet = get_request_file(request, path)
    write_overview(overview_sheet, request)

    # Get Data and write to new sheet
    data = pd.concat([await w.get_final() for w in warehouses])
    data_sheet = write_data_sheet(data, request.get('name'))

    ods.backup = False
    ods.saveas(path)
    LOGGER.info(f"Successfully wrote to sheet {data_sheet.name} @ {path}")

def get_request_file(request: dict[str, str], path:Path) -> Tuple[PackagedDocument, Sheet]:
    overview_sheet = None
    if path.exists():
        ods: FlatXMLDocument = opendoc(path)
        for idx, name in enumerate(ods.sheets.names()):
            if str(datetime.date.today().year) == name:
                overview_sheet = ods.sheets[idx]
    else:
        ods: PackagedDocument = newdoc("ods", path)
    if not overview_sheet:
        overview_sheet = init_overview_sheet(request)
        ods.sheets.insert(0, overview_sheet)
    return ods, overview_sheet

def init_overview_sheet(request: dict[str, str]):
    conf = request_conf.get('form')
    sheet = Sheet(str(datetime.date.today().year), size=(1, 20))
    # Write Column Headers
    for count, key in enumerate(request.keys()):
        c:Cell = sheet[0, count]
        c.set_value(str(conf.get(key)))
    return sheet

def write_overview(sheet:Sheet, request: dict[str, str]) -> None:
    # Write to overview
    #TODO sort by date and insert there
    for row in sheet.rows():
        print([cell.value for cell in row])
    current_rows = sheet.nrows()
    sheet.append_rows(1)
    for col_idx, value in enumerate(request.values()):
        cell = sheet.get_cell((current_rows, col_idx))
        if isinstance(value, datetime.date):
            cell.set_value(f"{value.strftime('%d.%m.%Y')}")
            continue
        cell.set_value(str(value) if value is not None else "")

def write_data_sheet(df:DataFrame, name:str) -> Sheet:
    conf = request_conf.get('form')
    # Add new Sheet
    data_sheet = Sheet(name,  size=(len(df)+1, len(df.columns)))

    # Write the header
    for col_idx, col_name in enumerate(df.columns):
        cell = data_sheet[0, col_idx]
        cell.set_value(str(col_name))

    # Write the data
    for row_idx, (index, row) in enumerate(df.iterrows(), start=1):
        for col_idx, value in enumerate(row):
            cell = data_sheet[row_idx, col_idx]
            cell.set_value(str(value) if value is not None else "")

    return data_sheet
