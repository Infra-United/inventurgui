# read ods file to get inventory data
import asyncio
import datetime
from pathlib import Path
from typing import Self

from webdav4.client import Client, ClientError
from dateutil.utils import today
from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
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
    instance = None

    def __init__(self, remote_dir: str, ncs: NextcloudSettings = NextcloudSettings()):
        self._domain = ncs.domain
        self._user = ncs.user
        self._webdav_url = f"https://{self._domain}/remote.php/dav/files/{self._user}"
        self.remote_dir = remote_dir
        super().__init__(self._webdav_url, auth=(self._user, ncs.token))

    @classmethod
    def singleton(cls) -> Self:
        if not cls.instance:
            cls.instance = Nextcloud(remote_dir=settings.cloud["dir"])
        return cls.instance

    @staticmethod
    def get_mod_time(path: Path) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(path.stat().st_mtime)

    @staticmethod
    def shut_down_if_missing_file(path: Path) -> None:
        if not path.is_file():
            LOGGER.exception(f"\nFile: >>>{path}<<< does not exist.\n Shutting down.")
            exit(1)

    def pull_file(self, key:str, file: str) -> None:
        if key is 'inventory' or 'logo':
            local = get_path(Path(file).name)
        else:
            local = get_path(Path(file).name, "pages" )
        remote = "/".join((self.remote_dir, file))
        try:
            if local.is_file() and self.get_mod_time(local).date() == today().date():
                LOGGER.info(f"{file} is up to date. Using cached data.")
                return
            if self.exists(remote):
                LOGGER.debug(f"Getting Data from {remote}...")
                self.download_file(remote, local)
            else:
                LOGGER.exception(
                    f"\nFile: >>>{remote}<<< does not exist in remote location.\n"
                    f"Checked in {self._webdav_url}.\nPlease review config."
                )
                self.shut_down_if_missing_file(local)
        except ():
            LOGGER.warning(f"Cannot connect to {self._domain}.\nPlease check your Internet Connection.")
            self.shut_down_if_missing_file(local)

    def push_file(self, file: Path) -> None:
        self.upload_file(get_path(file.name), "/".join((self.remote_dir, file.name)), overwrite=True)
        print(self.info("/".join((self.remote_dir, file.name))))
        LOGGER.info(f"Successfully pushed {file.name} to remote directory.")
