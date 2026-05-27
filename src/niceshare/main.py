import locale
import os

import jwt
from _duckdb import IOException, CatalogException
from nicegui import ui, app

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.database import DB
from niceshare.io.importer import read_inventory
from niceshare.io.selection import Selection
from niceshare.ui.helper.markdown import read_page_files
from niceshare.ui.root import root


# Starts the UI
def main():
    selections: list[Selection] = []
    for sheet in settings.data["warehouses"]:
        try:
            selection: Selection = DB.load(sheet, "inventory")
        except IOException, CatalogException:
            LOGGER.warning(f"Could not load {sheet} from database. Trying to import it.")
            selection: Selection = read_inventory(sheet)
            DB.save(selection.name, selection.inventory, "inventory")
        selections.append(selection)
    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    pages: dict[str, str] = {k: v for k, v in read_page_files()}
    locale.setlocale(locale.LC_TIME, settings.locale)
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    os.environ.setdefault("NICEGUI_STORAGE_PATH", str(get_path("users")))
    app.add_static_file(local_file=get_path("manifest.json"), url_path="/helpers/manifest.json", strict=False)
    app.add_static_file(local_file=get_path("service_worker.js"), url_path="/helpers/service_worker.js", strict=False)
    app.add_static_file(local_file=get_path("favicon.png"), url_path="/favicon.ico", strict=False)
    app.add_static_files("/splash/", get_path("splash"))
    app.add_static_files("/icons/", get_path("icons"))
    ui.run(
        root=lambda: root(selections, pages),
        language=settings.language,
        uvicorn_logging_level="debug" if ARGS.debug else "info",
        show=False,
        reload=ARGS.reload,
        uvicorn_reload_dirs=str(get_path("").parent.joinpath("src")),
        title=settings.title,
        favicon=get_path(settings.favicon),
        port=settings.port,
        uvicorn_reload_excludes=str(get_path("")),
        storage_secret=storage_secret if storage_secret else "12341232312",
    )
    LOGGER.debug("Successfully started UI.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
