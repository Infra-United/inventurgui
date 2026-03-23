from pathlib import Path

import polars as pl
from xlsxwriter import Workbook

from inventurgui.helper.config import settings
from inventurgui.helper.dates import convert_dates
from inventurgui.helper.i18n import i18n
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse


async def handle_request(
    request: dict[str, str | dict[str, str]], warehouses: list[Warehouse], delete: bool = False) -> None:
    start, end, month, year = convert_dates(request.get("dates"))
    path = get_path(f"{settings.requests['filename']}-20{year}.xlsx")

    # Create or Extend Overview
    with (Workbook(path, {'strings_to_numbers': True, 'default_date_format': settings.date_format, 'in_memory': True}) as wb):
        # Write Overview (Metadata)
        sheets = {}
        name_col = settings.form["input"].get("name")
        if not path.is_file():
            overview = write_overview(request)
        else:
            sheets = pl.read_excel(path, sheet_id=0)
            if delete:
                overview = sheets[f"20{year}"].join(write_overview(request), on=name_col, how='anti')
            else:
                overview = sheets[f"20{year}"].extend(write_overview(request))
                overview = overview.unique(name_col, keep='last').sort(pl.col(i18n.get("form.start")))
        overview.write_excel(wb, worksheet=wb.add_worksheet(f"20{year}"), autofit=True)

        # Get Data and write to new sheet
        if delete:
            sheets.pop(request.get("name"))
            request.update({"finish": i18n.get("finish.deleted")})
        else:
            dfs = [await w.get_final() for w in warehouses]
            df = pl.concat([df for df in dfs if df is not None], how="align")
            if request.get("name") in sheets.keys():
                request.update({"finish": i18n.get("finish.updated")})
            else:
                request.update({"finish": i18n.get("finish.success")})
            sheets.update({request.get("name"): df})

        # Write Requests
        for name in overview.select(pl.col(name_col)).to_series().to_list():
            if ws:= wb.get_worksheet_by_name(name):
                ws.table_cells.clear()
                sheets.get(name).write_excel(wb, worksheet=ws, autofit=True, float_precision=1)
            else:
                sheets.get(name).write_excel(wb, worksheet=wb.add_worksheet(name), autofit=True, float_precision=1)

    LOGGER.info(f"Successfully wrote request to {path}")
    Nextcloud.singleton().push_file(path)

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

async def write_download_list(path: Path, warehouses: list[Warehouse]):
    path.unlink(missing_ok=True)
    LOGGER.info(f"Creating download list file @{path}")
    with Workbook(path) as wb:
        for w in warehouses:
            df = await w.get_final()
            if df is None:
                continue
            LOGGER.debug(f"Creating download list sheet {w.name} @{path}")
            df.write_excel(
                workbook=wb, worksheet=w.name, autofit=True, float_precision=1, table_style="Table Style Medium 4"
            )
