from dataclasses import dataclass

import pandas as pd
from ezodf import opendoc, Sheet, newdoc
from ezodf.document import FlatXMLDocument, PackagedDocument
from nicegui import app
from pandas import Series

from inventurgui.helper.config import config, get_path, request_conf
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse


@dataclass
class Request:
    name: str = ''
    place: str = ''
    start: str = ''
    end: str = ''
    email: str = ''
    donation: str = ''
    message: str = ''
    checkbox: bool = False
    conf = request_conf.get('form')
    path = get_path(config['cloud']['push']['requests'])

    @property
    def subject(self) -> str:
        return f"[{self.name}] {self.start} - {self.end}"

    @property
    def html(self) -> str:
        html = ""
        for key, value in self.__dict__.items():
            if key == 'message':
                continue
            html += f"</br>{self.conf.get(key)}: {value}"

        html += f"\n\n{self.message}"
        return html

    async def write(self, warehouses:list[Warehouse]) -> None:
        LOGGER.info(f"Writing to file {self.path}")
        if self.path.exists():
            ods: FlatXMLDocument = opendoc(self.path)
        else:
            ods: PackagedDocument = newdoc("ods", self.path)

        df = pd.concat(await w.get_final() for w in warehouses)

        # Add new Sheet
        sheet = Sheet(self.name,  size=(len(df)+1, len(df.columns)))
        ods.sheets += sheet

        # Write the header
        for col_idx, col_name in enumerate(df.columns):
            cell = sheet[0, col_idx]
            cell.set_value(str(col_name))

        # Write the data
        for row_idx, (index, row) in enumerate(df.iterrows(), start=1):
            for col_idx, value in enumerate(row):
                cell = sheet[row_idx, col_idx]
                cell.set_value(str(value) if value is not None else "")

        ods.saveas(self.path)
        LOGGER.info(f"Successfully wrote to sheet {sheet.name} @ {self.path}")
