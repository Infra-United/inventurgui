# read ods file to get inventory data
from logging import debug
from pathlib import Path
from urllib.parse import quote

from aiowebdav.client import Client
from pandas import DataFrame
from pandas_ods_reader import read_ods
from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import get_path
from inventurgui.helper.logger import LOGGER


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
    data: DataFrame
    data_path: Path

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

    async def __post_init__(self):
        await self.get_inventory()
        self.read_inventory()

    async def get_inventory(self) -> None:
        if await self.check(self.data_path):
            await self.download_file(self.data_path, get_path(Path(self.data_path).name))
            await self.list(self.data_path, get_info=True)
        else:
            LOGGER.exception(f"\nFile: >>>{self.data_path}<<< does not exist.\n"
                             f"Checked in {self._webdav_url}.\nPlease review config.")
            await self.close()
            exit(1)

    def read_inventory(self) -> None:
        LOGGER.debug(f"Reading Data from {self.data_path}...")
        self.data = read_ods(get_path(Path(self.data_path).name))