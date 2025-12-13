# read ods file to get inventory data
import asyncio
import datetime
from pathlib import Path

from aiowebdav2.client import Client
from aiowebdav2.exceptions import ConnectionExceptionError
from dateutil.utils import today
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
    def __init__(self, remote_dir:str, ncs: NextcloudSettings = NextcloudSettings()):
        self._domain = ncs.domain
        self._user = ncs.user
        self._webdav_url = f"https://{self._domain}/remote.php/dav/files/{self._user}"
        self.remote_dir = remote_dir
        super().__init__(self._webdav_url, self._user, ncs.token)

    @staticmethod
    def get_mod_time(path: Path) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(path.stat().st_mtime)

    async def shut_down_if_missing_file(self, path:Path) -> None:
        if not path.is_file():
            LOGGER.exception(f"\nFile: >>>{path}<<< does not exist.\n Shutting down.")
            await self.close()
            exit(1)

    async def update_file(self, file:str) -> None:
        local = get_path(Path(file).name)
        remote = "/".join((self.remote_dir, file))
        try:
            if local.is_file() and self.get_mod_time(local).date() == today().date():
                LOGGER.info(f"{file} is up to date. Using cached data.")
                return
            if await self.check(remote):
                LOGGER.debug(f"Getting Data from {remote}...")
                await self.download_file(remote, local)
            else:
                LOGGER.exception(f"\nFile: >>>{remote}<<< does not exist in remote location.\n"
                                 f"Checked in {self._webdav_url}.\nPlease review config.")
                await self.shut_down_if_missing_file(local)
        except asyncio.TimeoutError, ConnectionExceptionError:
            LOGGER.warning(f"Cannot connect to {self._domain}.\nPlease check your Internet Connection.")
            await self.shut_down_if_missing_file(local)
