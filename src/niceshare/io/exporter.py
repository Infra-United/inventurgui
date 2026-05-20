from xlsxwriter import Workbook

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.database import DB
from niceshare.io.excel import write_sheet
from niceshare.io.nextcloud import Nextcloud
from niceshare.io.warehouse import Warehouse


def export_inventory(warehouses:list[Warehouse]):
    path = get_path(f"{settings.data_filename}.xlsx")
    with Workbook(path, {'strings_to_numbers': True, 'default_date_format': settings.date_format}) as workbook:
        for warehouse in warehouses:
            DB.save(warehouse.name, warehouse.inventory, "inventory")
            worksheet = workbook.add_worksheet(warehouse.name)
            write_sheet(warehouse.inventory.drop("index"), worksheet, workbook)
    LOGGER.info(f"Successfully wrote request to {path}")
    Nextcloud.singleton().push_file(path)
