import datetime
from math import nan
from os import mkdir
from pathlib import Path
from typing import Tuple

import pandas as pd
from ezodf import opendoc, Sheet, newdoc, Cell
from ezodf.document import FlatXMLDocument, PackagedDocument
from nicegui import app
from pandas import DataFrame, isna, notna

from inventurgui.helper.config import config, get_path, form
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse

async def write_ods(request: dict[str, str|dict[str, str]], warehouses: list[Warehouse]) -> None:
    path = get_path(config['cloud']['push']['requests'])

    start, end, month, year = convert_dates(request.get('dates'))
    # Get or create doc and overview_sheet
    ods, overview_sheet, data_sheet = get_request_file(request, path, f"20{year}")
    write_overview(overview_sheet, request)

    # Get Data and write to new sheet
    dfs = [await w.get_final() for w in warehouses]
    df = pd.concat(df for df in dfs if df is not None)
    if not data_sheet:
        data_sheet = Sheet(request.get('name'), size=(len(df) + 1, len(df.columns)))
    else:
        rows = (len(df) + 1) - data_sheet.nrows()
        if rows >= 1:
            data_sheet.append_rows(rows)
        cols = (len(df.columns) + 1) - data_sheet.ncols()
        if cols >= 1:
            data_sheet.append_columns(cols)
    data_sheet = write_data_sheet(df, data_sheet)
    ods.sheets += data_sheet

    ods.save()
    LOGGER.info(f"Successfully wrote to sheet {data_sheet.name} @ {path}")

def get_request_file(request: dict[str, str], path:Path, year:str) -> Tuple[PackagedDocument, Sheet, Sheet|None]:
    overview_sheet = None
    data_sheet: Sheet|None = None
    if path.is_file():
        LOGGER.debug(f"Found existing request file @{path}.")
        ods: FlatXMLDocument = opendoc(path)
        for idx, name in enumerate(ods.sheets.names()):
            if year == name:
                overview_sheet = ods.sheets[idx]
            if name == request.get('name'):
                data_sheet = ods.sheets[idx]
    else:
        LOGGER.debug(f"Couldn't find request file @{path} - creating it.")
        ods: PackagedDocument = newdoc("ods", path)
    if not overview_sheet:
        LOGGER.debug(f"Couldn't find overview sheet for {year} - creating it.")
        overview_sheet = init_overview_sheet(request, year)
        ods.sheets.insert(0, overview_sheet)
    ods.backup = False
    ods.save()
    return ods, overview_sheet, data_sheet

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
            case 'message' | 'sent' | 'updated':
                continue
            case _:
                c:Cell = sheet[0, count]
                c.set_value(f"{form['input'].get(key)}")
                count += 1
    sheet[0, count].set_value(str(form.get('sent')))
    sheet[0, count+1].set_value(str(form.get('updated')))
    LOGGER.info(f"Successfully created overview sheet for year {year}.")
    return sheet

def write_overview(sheet:Sheet, request: dict[str, str|dict[str, str]]) -> None:
    # Write to overview
    LOGGER.debug(f"Writing request to overview sheet...")
    start, end, month, year = convert_dates(request.get('dates'))
    row_number = find_row_by_name_or_start(sheet, start, request.get('name'))
    count = 0
    for key, value in request.items():
        match key:
            case 'dates':
                for i, val in enumerate([month, start, end]):
                    cell:Cell = sheet.get_cell((row_number, i))
                    cell.set_value(str(val))
                count += 3
                continue
            case 'message':
                continue
            case _:
                cell:Cell = sheet.get_cell((row_number, count))
                cell.set_value(str(value) if value and notna(value) else "")
                count += 1
    LOGGER.info(f"Successfully wrote request to overview sheet @ row: {row_number}.")

def write_data_sheet(df:DataFrame, data_sheet:Sheet) -> Sheet:
    LOGGER.debug(f"Writing request to data sheet...")
    # Write the header
    for col_idx, col_name in enumerate(df.columns):
        cell = data_sheet[0, col_idx]
        cell.set_value(str(col_name))

    # Write the data
    try:
        for row_idx, (index, row) in enumerate(df.iterrows(), start=1):
            for col_idx, value in enumerate(row):
                cell = data_sheet[row_idx, col_idx]
                cell.set_value(str(value) if value and notna(value) else "")
    except IndexError:
        LOGGER.exception(f"{row_idx, col_idx} out of range.")

    LOGGER.info("Successfully wrote request to data sheet.")
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

def find_row_by_name_or_start(sheet:Sheet, start:str, name:str) -> int:
    LOGGER.debug(f"Finding row number by name or start...")
    count = 0
    start = datetime.date.strptime(start, config['date_format'])
    insert_count = None
    for row in sheet.rows():
        try:
            row_start = datetime.date.strptime(row[1].value, config['date_format'])
            row_name = str(row[3].value)
        except ValueError:
            count += 1
            continue
        if name == row_name:
            LOGGER.info(f"Found existing entry for this request @ row number {count}! Updating entry...")
            return count
        if start < row_start:
            insert_count = count
        count += 1
    LOGGER.info("Could not find entry for this request! Creating new entry...")
    if not insert_count:
        insert_count = sheet.nrows()
        sheet.append_rows()
        return insert_count
    else:
        sheet.insert_rows(insert_count)
        return insert_count

async def write_download_list(filename:Path, warehouses:list[Warehouse]):
    if not get_path('/lists/').is_dir():
        mkdir(get_path('/lists/'))
    request = app.storage.user.get('form')
    LOGGER.debug(f"Writing list for download...")
    ods: PackagedDocument = newdoc("ods", filename)
    for w in warehouses:
        df = await w.get_final()
        if df is None or df.empty:
            continue
        df.drop(columns=[config['warehouse']['label']], inplace=True)
        data_sheet = Sheet(w.name, size=(len(df) + 1, len(df.columns)))
        ods.sheets += write_data_sheet(df,data_sheet)
    ods.backup = False
    ods.saveas(filename)