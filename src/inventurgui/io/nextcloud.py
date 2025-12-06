# read ods file to get inventory data
import asyncio
import datetime
from pathlib import Path
from typing import List

import ezodf
from aiowebdav.client import Client
from aiowebdav.exceptions import NoConnection
from pandas_ods_reader import read_ods
from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import get_path, config
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse


class NextcloudSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="UTF-8",
        env_prefix="NEXTCLOUD_",
        extra="ignore",
    )
    domain: str
    user: str
    token: str

class Nextcloud(Client):
    inventory_path: str

    def __init__(self, ncs: NextcloudSettings = NextcloudSettings()):
        self._domain = ncs.domain
        self._user = ncs.user
        self._webdav_url = f"https://{self._domain}/remote.php/dav/files/{self._user}"
        options = {
            'webdav_hostname': self._webdav_url,
            'webdav_login': self._user,
            'webdav_password': ncs.token,
        }
        super().__init__(options)


    @property
    def inventory_file(self) -> Path:
        return get_path(Path(self.inventory_path).name)

    @property
    def warehouses(self) -> List[Warehouse]:
        warehouses = []
        LOGGER.debug(f"Reading Data from {self.inventory_file}...")
        for sheet_num, sheet in enumerate(ezodf.opendoc(self.inventory_file).sheets):
            if sheet_num < config['data']['sheets']:
                LOGGER.debug(f"Reading sheet {sheet.name}...")
                warehouses.append(Warehouse(name=sheet.name, inventory=read_ods(self.inventory_file, sheet_num + 1)))
        return warehouses

    @staticmethod
    def get_mod_time(path: Path) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(path.stat().st_mtime)

    async def shut_down_if_missing_file(self, path:Path) -> None:
        if not path.is_file():
            LOGGER.exception(f"\nFile: >>>{path}<<< does not exist.\n Shutting down.")
            await self.close()
            exit(1)

    async def update_inventory(self) -> None:
        try:
          #  if self.inventory_file.is_file() and self.get_mod_time(self.inventory_file).date() == today().date():
           #     LOGGER.info(f"Inventory file is up to date. Using cached data.")
            #    return
            LOGGER.debug(f"Getting Data from {self.inventory_path}...")
            if await self.check(self.inventory_path):
                await self.download_file(self.inventory_path, self.inventory_file)
            else:
                LOGGER.exception(f"\nFile: >>>{self.inventory_path}<<< does not exist in remote location.\n"
                                 f"Checked in {self._webdav_url}.\nPlease review config.")
                await self.shut_down_if_missing_file(self.inventory_file)
        except asyncio.TimeoutError, NoConnection:
            LOGGER.warning(f"Cannot connect to {self._domain}.\nPlease check your Internet Connection.")
            await self.shut_down_if_missing_file(self.inventory_file)