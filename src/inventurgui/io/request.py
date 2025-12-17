import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

import pandas as pd
from ezodf import opendoc, Sheet, newdoc, Cell
from ezodf.document import FlatXMLDocument, PackagedDocument
from pandas import DataFrame

from inventurgui.helper.config import config, get_path, request_conf, form
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse

async def write_ods(request: dict[str, str|dict[str, str]], warehouses: list[Warehouse]) -> None:
    path = get_path(config['cloud']['push']['requests'])
    LOGGER.info(f"Writing to file {path}")

    start, end, month, year = convert_dates(request.get('dates'))

    # Get or create doc and overview_sheet
    ods, overview_sheet = get_request_file(request, path, f"20{year}")
    write_overview(overview_sheet, request)

    # Get Data and write to new sheet
    data = pd.concat([await w.get_final() for w in warehouses])
    data_sheet = write_data_sheet(data, request.get('name'))
    ods.sheets += data_sheet

    ods.backup = False
    ods.saveas(path)
    LOGGER.info(f"Successfully wrote to sheet {data_sheet.name} @ {path}")

def get_request_file(request: dict[str, str], path:Path, year:str) -> Tuple[PackagedDocument, Sheet]:
    overview_sheet = None
    if path.exists():
        ods: FlatXMLDocument = opendoc(path)
        for idx, name in enumerate(ods.sheets.names()):
            if year == name:
                overview_sheet = ods.sheets[idx]
    else:
        ods: PackagedDocument = newdoc("ods", path)
    if not overview_sheet:
        overview_sheet = init_overview_sheet(request, year)
        ods.sheets.insert(0, overview_sheet)
    return ods, overview_sheet

def init_overview_sheet(request: dict[str, str|dict[str,str]], year:str):
    sheet = Sheet(str(year), size=(1, 20))
    # Write Column Headers
    count = 0
    for key in request.keys():
        match key:
            case 'dates':
                for i, val in enumerate(['month', 'start', 'end']):
                    cell = sheet.get_cell((0, i))
                    cell.set_value(str(form.get(val)))
                count += 3
                continue
            case 'message':
                continue
            case _:
                value = f"{form['input'].get(key)}"
                c:Cell = sheet[0, count]
                c.set_value(value)
                count += 1
    return sheet

def write_overview(sheet:Sheet, request: dict[str, str|dict[str, str]]) -> None:
    # Write to overview
    start, end, month, year = convert_dates(request.get('dates'))
    row_number = find_row_by_start(sheet, start)
    sheet.insert_rows(row_number)
    count = 0
    for key, value in request.items():
        match key:
            case 'dates':
                for i, val in enumerate([month, start, end]):
                    cell = sheet.get_cell((row_number, i))
                    cell.set_value(str(val))
                count += 3
                continue
            case 'message':
                continue
            case _:
                f"{form['input'].get(key)}: {value}"
        cell = sheet.get_cell((row_number, count))
        cell.set_value(str(value) if value is not None else "")
        count += 1

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

def convert_dates(dates:str|dict[str,str]) -> Tuple[str,str, str, str]:
    """
    Converts the dates supplied from a date_range_picker to the configured format.
    Also returns the month (%B) and year (%y) of the range.
    See https://strftime.org/ for more information.
    :param dates: {'from': start, 'to': end}
    :return: start, end, month, year
    """
    if isinstance(dates, dict):
        start = dates.get('from')
        end = dates.get('to')
    else:
        start = dates
        end = dates
    start = datetime.date.fromisoformat(start)
    end = datetime.date.fromisoformat(end)
    year = f"{start:%y}/{end:%y}" if not start.year == end.year else f"{start:%y}"
    month = f"{start:%B}/{end:%B}" if not start.month == end.month else f"{start:%B}"
    start = start.strftime(config['date_format'])
    end = end.strftime(config['date_format'])
    return start, end, month, year

def find_row_by_start(sheet:Sheet, start:str) -> int|None:
    count = 0
    start = datetime.date.strptime(start, config['date_format'])
    for row in sheet.rows():
        try:
            row_start = datetime.date.strptime(row[1].value, config['date_format'])
            print(row_start)
        except ValueError:
            count += 1
            continue
        if start < row_start:
            return count
        count += 1
    return sheet.nrows()