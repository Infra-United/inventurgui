import datetime
from dataclasses import dataclass, field

import pandas as pd
from ezodf import opendoc, Sheet, newdoc, Cell
from ezodf.document import FlatXMLDocument, PackagedDocument

from inventurgui.helper.config import config, get_path, request_conf
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse


@dataclass
class Request:
    name: str
    place: str
    start: datetime.date
    end: datetime.date
    email: str
    donation: str
    conf = request_conf.get('form')
    path = get_path(config['cloud']['push']['requests'])

    @classmethod
    def from_dict(cls, bind: dict) -> Request:
        print(type(bind.get('start')))
        return Request(bind.get('name'), bind.get('place'),
                datetime.date.fromisoformat(bind.get('start')),
                datetime.date.fromisoformat(bind.get('start')),
                bind.get('email'),
                bind.get('donation'))

    @property
    def subject(self) -> str:
        return f"[{self.name}] {self.start} - {self.end}"

    def html(self, message) -> str:
        html = ""
        for key, value in self.__dict__.items():
            if isinstance(value, datetime.date):
                html += f"</br>{self.conf.get(key)}: {f"{value.strftime('%d.%m.%Y')}"}"
            html += f"</br>{self.conf.get(key)}: {value}"
        html += f"\n\n{message}"
        return html

    async def write_ods(self, warehouses:list[Warehouse]) -> None:
        def init_overview_sheet():
            sheet = Sheet(str(datetime.date.today().year), size=(1, 20))
            # Write Column Headers
            for count, key in enumerate(self.__dict__.keys()):
                c:Cell = sheet[0, count]
                c.set_value(str(self.conf.get(key)))
            return sheet

        LOGGER.info(f"Writing to file {self.path}")
        # Get or create doc and overview_sheet
        overview_sheet = None
        if self.path.exists():
            ods: FlatXMLDocument = opendoc(self.path)
            for idx, name in enumerate(ods.sheets.names()):
                if str(datetime.date.today().year) == name:
                    overview_sheet = ods.sheets[idx]
        else:
            ods: PackagedDocument = newdoc("ods", self.path)
        if not overview_sheet:
            overview_sheet = init_overview_sheet()
            ods.sheets.insert(0, overview_sheet)

        # Write to overview
        #TODO sort by date and insert there
        for row in overview_sheet.rows():
            print(cell for cell in row)
        current_rows = overview_sheet.nrows()
        overview_sheet.append_rows(1)
        for col_idx, value in enumerate(self.__dict__.values()):
            cell = overview_sheet.get_cell((current_rows, col_idx))
            if isinstance(value, datetime.date):
                cell.set_value(f"{value.strftime('%d.%m.%Y')}")
                continue
            cell.set_value(str(value) if value is not None else "")

        # Get Data
        df = pd.concat([await w.get_final() for w in warehouses])

        # Add new Sheet
        data_sheet = Sheet(self.name,  size=(len(df)+1, len(df.columns)))
        ods.sheets += data_sheet

        # Write the header
        for col_idx, col_name in enumerate(df.columns):
            cell = data_sheet[0, col_idx]
            cell.set_value(str(col_name))

        # Write the data
        for row_idx, (index, row) in enumerate(df.iterrows(), start=1):
            for col_idx, value in enumerate(row):
                cell = data_sheet[row_idx, col_idx]
                cell.set_value(str(value) if value is not None else "")

        ods.saveas(self.path)
        LOGGER.info(f"Successfully wrote to sheet {data_sheet.name} @ {self.path}")
