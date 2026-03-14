import datetime
from contextlib import suppress
from pathlib import Path
from typing import Tuple

import polars as pl
from ezodf import opendoc, Sheet, newdoc, Cell
from ezodf.document import FlatXMLDocument, PackagedDocument
from polars import DataFrame
from xlsxwriter import Workbook

from inventurgui.helper.config import settings
from inventurgui.helper.dates import convert_dates
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse


#Todo maybe write to excel instead and separate files per year

async def save_request(
    request: dict[str, str | dict[str, str]], warehouses: list[Warehouse], update: bool = False
) -> None:
    path = get_path(settings.cloud["push"]["requests"])

    start, end, month, year = convert_dates(request.get("dates"))
    # Get or create doc and overview_sheet
    ods, overview_sheet, data_sheet = get_request_file(request, path, f"20{year}")
    row_number = find_row_by_name_or_start(overview_sheet, start, request.get("name"), name_only=update)
    write_overview(overview_sheet, request, row_number)

    # Get Data and write to new sheet
    dfs = [await w.get_final() for w in warehouses]
    df = pl.concat([df for df in dfs if df is not None], how='align')
    if not data_sheet:
        data_sheet = Sheet(request.get("name"), size=(len(df) + 1, len(df.columns)))
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
    Nextcloud.singleton().push_file(path)

async def delete_request(request: dict[str, str | dict[str, str]]) -> None:
    path = get_path(settings.cloud["push"]["requests"])
    start, end, month, year = convert_dates(request.get("dates"))
    ods, overview_sheet, data_sheet = get_request_file(request, path, f"20{year}")
    row_number = find_row_by_name_or_start(overview_sheet, start, request.get("name"), name_only=True)
    overview_sheet.delete_rows(row_number)
    with suppress(AttributeError):
        del ods.sheets[data_sheet.name]
    ods.save()
    with suppress(FileNotFoundError):
        Path(request.get("download")).unlink()
    Nextcloud.singleton().push_file(path)


def get_request_file(request: dict[str, str], path: Path, year: str) -> Tuple[PackagedDocument, Sheet, Sheet | None]:
    overview_sheet = None
    data_sheet: Sheet | None = None
    if path.is_file():
        LOGGER.debug(f"Found existing request file @{path}.")
        ods: FlatXMLDocument = opendoc(path)
        for idx, name in enumerate(ods.sheets.names()):
            if year == name:
                overview_sheet = ods.sheets[idx]
            if name == request.get("name"):
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


def init_overview_sheet(request: dict[str, str | dict[str, str]], year: str):
    form: dict[str, str | dict[str, str]] = settings.form
    sheet = Sheet(str(year), size=(1, 20))
    # Write Column Headers
    count = 0
    for key in request.keys():
        match key:
            case "dates":
                for i, val in enumerate(["month", "start", "end"]):
                    cell = sheet.get_cell((0, i))
                    cell.set_value(str(form.get(val)))
                count += 3
                continue
            case "message":
                continue
            case _:
                if key in form["input"].keys():
                    c: Cell = sheet[0, count]
                    c.set_value(f"{form['input'].get(key)}")
                    count += 1
    sheet[0, count].set_value(str(form.get("sent")))
    sheet[0, count + 1].set_value(str(form.get("updated")))
    LOGGER.info(f"Successfully created overview sheet for year {year}.")
    return sheet


def write_overview(sheet: Sheet, request: dict[str, str | dict[str, str]], row_number: int) -> None:
    # Write to overview
    LOGGER.debug("Writing request to overview sheet...")
    start, end, month, year = convert_dates(request.get("dates"))
    count = 0
    for key, value in request.items():
        match key:
            case "dates":
                for i, val in enumerate([month, start, end]):
                    cell: Cell = sheet.get_cell((row_number, i))
                    cell.set_value(str(val))
                count += 3
                continue
            case "message" | "finish" | "download":
                continue
            case _:
                cell: Cell = sheet.get_cell((row_number, count))
                cell.set_value(str(value) if value else "")
                count += 1
    LOGGER.info(f"Successfully wrote request to overview sheet @ row: {row_number}.")


def write_data_sheet(df: DataFrame, data_sheet: Sheet) -> Sheet:
    LOGGER.debug("Writing request to data sheet...")
    # Write the header
    for col_idx, col_name in enumerate(df.columns):
        cell = data_sheet[0, col_idx]
        cell.set_value(str(col_name))

    # Write the data
    try:
        for row_idx, row in enumerate(df.iter_rows(), start=1):
            for col_idx, value in enumerate(row):
                cell = data_sheet[row_idx, col_idx]
                cell.set_value(str(value) if value else "")
    except IndexError:
        LOGGER.exception(f"{row_idx, col_idx} out of range.")

    LOGGER.info("Successfully wrote request to data sheet.")
    return data_sheet


def find_row_by_name_or_start(sheet: Sheet, start: str, name: str, name_only) -> int:
    LOGGER.debug("Finding row number by name or start...")
    count = 0
    start = datetime.date.strptime(start, settings.date_format)
    insert_count = None
    for row in sheet.rows():
        try:
            row_start = datetime.date.strptime(row[1].value, settings.date_format)
            row_name = str(row[3].value)
        except ValueError:
            count += 1
            continue
        if name == row_name:
            LOGGER.info(f"Found existing entry for this request @ row number {count}!")
            return count
        if start < row_start and not name_only:
            insert_count = count
        count += 1
    LOGGER.info("Could not find entry for this request!")
    if not insert_count:
        insert_count = sheet.nrows()
        sheet.append_rows()
        return insert_count
    else:
        sheet.insert_rows(insert_count)
        return insert_count


async def write_download_list(path: Path, warehouses: list[Warehouse]):
    path.unlink(missing_ok=True)
    LOGGER.info(f"Creating download list file @{path}")
    with Workbook(path) as wb:
        for w in warehouses:
            df = await w.get_final()
            if df is None:
                continue
            LOGGER.debug(f"Creating download list sheet {w.name} @{path}")
            df.write_excel(workbook=wb,
                           worksheet=w.name,
                           autofit=True,
                           float_precision=1,
                           table_style="Table Style Medium 4")
