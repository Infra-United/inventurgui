from contextlib import suppress
from pathlib import Path

import polars as pl
from polars import DataFrame
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from niceshare.helper.config import settings
from niceshare.helper.dates import convert_dates
from niceshare.helper.i18n import i18n
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.selection import Selection


async def handle_request(
    request: dict[str, str | dict[str, str]], warehouses: list[Selection], dl_path: Path, delete: bool = False
) -> DataFrame:
    start, end, month, year = convert_dates(request.get("dates"), string=False)
    path = get_path(f"{settings.requests['filename']}-20{year}.xlsx")
    sheets = {}
    name_col = settings.form["input"].get("name")
    request_name: str = request["name"]
    overview_name: str = f"20{year}"
    # Write Overview (Metadata)
    if not path.is_file():  # If it's the first request in this year
        overview = write_overview(request)
    else:  # Read all sheets and get overview sheet
        sheets: dict[str, DataFrame] = pl.read_excel(path, sheet_id=0, raise_if_empty=False)
        overview = list(sheets.values())[0]
        if overview.is_empty():
            overview = write_overview(request)
        elif delete:
            overview = overview.join(write_overview(request), on=name_col, how="anti")
        else:  # Append request
            overview = pl.concat(
                (
                    df.cast({settings.form["input"].get("donation"): pl.Int64})
                    for df in [overview, write_overview(request)]
                ),
                how="diagonal_relaxed",
            )
            # Unique drops any pre-existing rows with the same name (so it appears to be updated)
            overview = overview.unique(name_col, keep="last").sort(pl.col(i18n.get("form.start")))
    sheets.update({overview_name: overview})

    # Get Data and add request to sheets (updating if name already exists)
    dfs = [w.selected() for w in warehouses]
    df = pl.concat([df for df in dfs if df is not None], how="align")

    # TODO maybe move this back to submit function
    if request_name in sheets.keys() and not delete:  # Update
        request.update({"finish": i18n.get("finish.updated")})
    elif delete:
        request.update({"finish": i18n.get("finish.deleted")})
    else:  # Add
        request.update({"finish": i18n.get("finish.success")})

    sheets.update({request_name: df})

    # Find overlaps and add overlap column to each sheet accordingly
    # TODO Known Bug: If there is a request overlapping with more than one other request and this request gets deleted,
    #  the others are still marked as overlapping although they may or may not overlap each other
    sheets = find_overlaps(sheets, request, delete)

    if delete:
        sheets.pop(request_name)  # Needs to happen before writing but after finding overlaps
    else:  # Write excel file for download
        dl_path.unlink(missing_ok=True)
        data = sheets.get(request_name)
        LOGGER.info(f"Creating download list file @{dl_path}")
        names: list[str] = sorted(data[settings.selection["label"]].unique())
        with Workbook(dl_path) as dl_wb:
            for name in names:
                LOGGER.debug(f"Creating download list sheet {name} @{dl_path}")
                write_sheet(data.filter(pl.col(settings.selection["label"]) == name), dl_wb.add_worksheet(name), dl_wb)

    # Save to database
    # [DB.save(name, df, 'request') for name, df in sheets.items()]

    with Workbook(path, {"strings_to_numbers": True, "default_date_format": settings.date_format}) as workbook:
        # Write Overview
        worksheet = workbook.add_worksheet(overview_name)
        write_sheet(sheets[overview_name], worksheet, workbook)

        # Write Request Sheets
        for name in overview.select(pl.col(name_col)).to_series().to_list():
            if worksheet := workbook.get_worksheet_by_name(name):
                worksheet.table_cells.clear()
            else:
                worksheet = workbook.add_worksheet(name)
            write_sheet(sheets[name], worksheet, workbook)

    LOGGER.info(f"Successfully wrote request to {path}")
    return sheets[request_name]


def write_overview(request: dict[str, str | dict[str, str]]):
    # Write Column Headers
    df = pl.DataFrame()
    count = 0
    for key, value in request.items():
        match key:
            case "dates":
                start, end, month, year = convert_dates(request.get("dates"))
                for k, v in {"month": month, "start": start, "end": end}.items():
                    df.insert_column(count, pl.lit(v).alias(i18n.get(f"form.{k}")))
                    count += 1
                continue
            case "message":
                continue
            case _:
                if key in settings.form["input"].keys():
                    df.insert_column(count, pl.lit(value).alias(f"{settings.form['input'].get(key)}"))
                    count += 1
                elif key in i18n.get("mail"):
                    df.insert_column(count, pl.lit(value).alias(i18n.get(f"mail.{key}")))
                    count += 1
                elif key == "edit_link":
                    df.insert_column(count, pl.lit(value).alias(i18n.get("finish.editing_link")))
    LOGGER.info("Successfully created overview sheet.")
    return df


def write_sheet(df: DataFrame, ws: Worksheet, wb: Workbook):
    with suppress(AttributeError):
        backup = ws.table_cells
    try:
        if i18n.get("form.overlap") in df.columns:
            red = wb.add_format({"bg_color": "#FFC7CE"})
            for idx, row in enumerate(df.iter_rows(named=True)):
                if row[i18n.get("form.overlap")]:
                    ws.conditional_format(idx + 1, 0, idx + 1, len(df.columns), {"type": "no_blanks", "format": red})

        df.write_excel(wb, worksheet=ws, autofit=True, float_precision=1, header_format={"bold": True})
    except Exception:
        write_sheet(pl.from_dict(backup), ws, wb)


def find_overlaps(
    sheets: dict[str, DataFrame], request: dict[str, str | dict[str, str]], delete: bool
) -> dict[str, DataFrame]:
    # Check if to requests overlap timewise
    overview = list(sheets.values())[0]
    overlap = i18n.get("form.overlap")
    start, end, month, year = convert_dates(request["dates"], string=False)
    col_start = pl.col(i18n.get("form.start")).str.strptime(pl.Date, settings.date_format)
    col_end = pl.col(i18n.get("form.end")).str.strptime(pl.Date, settings.date_format)
    start_check_1 = pl.lit(start).is_between(col_start, col_end)
    start_check_2 = col_start.is_between(start, end)
    end_check_1 = col_end.is_between(start, end)
    end_check_2 = pl.lit(end).is_between(col_start, col_end)
    overlap_df = overview.filter(start_check_1 | start_check_2 | end_check_1 | end_check_2)
    if overlap in overview.columns:
        overlap_df = pl.concat([overlap_df, overview.filter(pl.col(overlap) == True)], how="diagonal_relaxed")
    overlap_names = overlap_df.select(settings.form["input"].get("name")).unique().to_series().to_list()

    # Check if the overlapping requests actually overlap in data
    # (Iterate over a copy because we modify the list in the loop)
    for overlap_name in overlap_names[:]:
        # If request already exists and is being updated skip it
        if overlap_name == request.get("name"):
            if len(overlap_names) == 1:
                with suppress(ValueError):
                    overlap_names.remove(overlap_name)
            continue
        other = sheets.get(request["name"])
        for name in [overlap_name, request.get("name")]:
            # Add overlap column (Updating existing)
            df = sheets.get(name)
            df = add_overlap_column(df, other, settings.columns.get("object"), delete)
            # if there are overlaps
            if df[overlap].any():
                overlap_names.append(name) if name not in overlap_names else None
                LOGGER.info(f"Found overlapping data for {request.get('name')} in {overlap_name}.")
                request.update({"overlap": i18n.get("finish.overlap")})
            else:
                overlap_names.remove(name) if name in overlap_names else None
                df = df.drop(overlap, strict=False)
            sheets.update({name: df})
            other = df

    overview = add_overlap_column(overview, overlap_names, settings.form["input"].get("name")).sort(col_start)
    sheets.update({f"20{year}": overview})

    return sheets


def add_overlap_column(df: DataFrame, other: DataFrame | list, col_to_match: str, delete: bool = False):
    # Update overlap column in "df" with matching objects in "other" (keep existing overlaps with other requests)
    overlap = i18n.get("form.overlap")
    if isinstance(other, DataFrame):
        is_in = other[col_to_match]
    else:
        is_in = other
    if overlap in df.columns:  # Update values in column
        df = df.with_columns(
            pl.when(pl.col(col_to_match).is_in(is_in))
            .then(pl.lit(True) if not delete else pl.lit(False))
            .otherwise(pl.col(overlap))
            .alias(overlap)
        ).sort(overlap, descending=True)
    else:  # Add overlap column
        df = df.with_columns(pl.col(col_to_match).is_in(is_in).alias(overlap)).sort(overlap, descending=True)
    return df
