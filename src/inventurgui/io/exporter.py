from xlsxwriter import Workbook

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.database import DB
from inventurgui.io.excel import write_sheet
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse


def export_inventory(warehouses:list[Warehouse]):
    path = get_path(f"{settings.data_filename}.xlsx")
    with Workbook(path, {'strings_to_numbers': True, 'default_date_format': settings.date_format}) as workbook:
        for warehouse in warehouses:
            DB.save(warehouse.name, warehouse.inventory, "inventory")
            worksheet = workbook.add_worksheet(warehouse.name)
            write_sheet(warehouse.inventory.drop("index"), worksheet, workbook)
    LOGGER.info(f"Successfully wrote request to {path}")
    Nextcloud.singleton().push_file(path)
