import asyncio
import locale
import os

import jwt
from nicegui import ui

from dataviewer.cli import ARGS
from dataviewer.helper.config import settings
from dataviewer.helper.logger import LOGGER
from dataviewer.io.importer import read_ods
# from dataviewer.io.nextcloud import Nextcloud
from dataviewer.io.selection import Selection
# from dataviewer.io.wiki import read_wiki, Wiki
from dataviewer.ui.helper.markdown import read_page_files
from dataviewer.ui.root import root


async def load_data() -> list[Selection]:
    # if DB.DB_FILE.is_file():
    #  selections: list[Selection] = [DB.load(sheet) for sheet in settings.data["warehouses"]]
    # else:
    selections: list[Selection] = [read_ods(sheet) for sheet in settings.data["warehouses"]]
    #  [DB.save(w.name, w.inventory) for w in selections]
    # [await handle_images(w.name, w.inventory) for w in selections]
    # ensure_directory_structure([w.name for w in selections])
    return selections


# Starts the UI
def main(selections: list[Selection]):
    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    locale.setlocale(locale.LC_TIME, settings.locale)
    LOGGER.debug("Getting pages")
    pages: dict[str, str] = {k: v for k, v in read_page_files()}
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    LOGGER.debug("Starting UI...")
    ui.run(
        # native=True,
        # fullscreen=True,
        root=lambda: root(selections, pages),
        language=settings.language,
        reload=ARGS.reload,
        title=settings.title,
        storage_secret=storage_secret if storage_secret else "12341232312",
    )
    LOGGER.debug("Successfully started UI.")


if __name__ in {"__main__", "__mp_main__"}:
    data = asyncio.run(load_data())
    main(data)
