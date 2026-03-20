import os

import jwt
from nicegui import ui, app

from inventurgui.cli import ARGS
from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path, ensure_directory_structure
from inventurgui.io.importer import read_inventory
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse
from inventurgui.io.wiki import read_wiki
from inventurgui.ui.helper.markdown import read_page_files
from inventurgui.ui.root import root


# Starts the UI
def main():
    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    display_wiki = settings.help["wiki"]
    if not ARGS.reload:
        Nextcloud.singleton().pull_files()
    warehouses: list[Warehouse] = [w for w in read_inventory()]
    ensure_directory_structure([w.name for w in warehouses])
    pages: dict[str, str] = {k: v for k, v in read_page_files()}
    if display_wiki:
        wiki = read_wiki()
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    os.environ.setdefault("NICEGUI_STORAGE_PATH", str(get_path("users")))
    app.add_static_files("/images", str(get_path("images")))
    ui.run(
        root=lambda: root(warehouses, pages, wiki if display_wiki else None),
        language=settings.language,
        uvicorn_logging_level="debug" if ARGS.debug else "info",
        show=False,
        reload=ARGS.reload,
        uvicorn_reload_dirs=str(get_path("").parent.joinpath("src")),
        title=settings.title,
        favicon=get_path(settings.favicon),
        port=settings.port,
        storage_secret=storage_secret if storage_secret else "12341232312",
    )
    LOGGER.debug("Successfully started UI.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
