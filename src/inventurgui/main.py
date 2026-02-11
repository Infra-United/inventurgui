import os
from os import mkdir

import ezodf
import jwt
from nicegui import ui, app
from i18n_modern import I18nModern
from pandas_ods_reader import read_ods

from inventurgui.cli import ARGS
from inventurgui.helper.config import settings, create_default_config
from inventurgui.helper.i18n import i18n
from inventurgui.helper.paths import get_path, ensure_dirs
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.layout import header, left_drawer, footer
from inventurgui.ui.markdown import get_markdown
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.finish import finish_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.sub_pages.login import login_page
from inventurgui.ui.sub_pages.start import start_page
from inventurgui.ui.sub_pages.warehouse import warehouse_page
from inventurgui.ui.theme import Theme


def root(warehouses:list[Warehouse], markdown:dict[str, str]):
    # Everytime a user loads the page this is executed - creates the layout - content is created by sub_pages.

    ui.add_head_html("""
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
        <script>
        function emitSize() {
            emitEvent('resize', {
                width: document.body.offsetWidth,
                height: document.body.offsetHeight,
            });
        }
        window.onload = emitSize;
        window.onresize = emitSize;
        </script>
    """)

    # Set colors
    Theme(settings.theme).set_colors()

    # Set default styles
    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll h-[calc(100vh-56px)]")
    ui.query(".nicegui-sub-pages").classes("bg-dark w-full h-[calc(100vh-56px)] no-scroll").style(replace="gap:0")

    # init app storage
    storage = Cache(warehouses)

    # Create Main Layout
    ld = left_drawer(warehouses)

    # Register Pages
    user_id = app.storage.browser["id"]
    pages = ui.sub_pages(data={"warehouses": warehouses, "ld": ld, "user_id": user_id, "storage": storage, 'md':markdown})
    pages.add("/", start_page)
    pages.add("/login", login_page)
    pages.add("/logout", login_page)
    pages.add(f"/{url_safe(settings.cart['label'])}", cart_page)
    pages.add(f"/{url_safe(settings.form['label'])}", form_page)
    pages.add(f"/{url_safe(settings.finish['label'])}", finish_page)
    pages.add(f"/{url_safe(settings.warehouse['label'])}", warehouse_page)

    # Register category sub_pages
    for warehouse in warehouses:
        warehouse = warehouse
        name = url_safe(warehouse.name)
        for category in warehouse.categories:
            pages.add(f"/{name}/{url_safe(category)}", lambda w=warehouse, c=category: category_page(c, w))
        if authenticate_user():
            pages.add(f"/{name}/{url_safe(i18n.get('admin.edits'))}", lambda w=warehouse, c=i18n.get('admin.edits'): category_page(c, w))

    header(ld)
    footer(ld)


#def backend():
#    nc = Nextcloud.singleton()
#    for key, file in config["cloud"]["pull"].items():
#        app.timer(60000, lambda f=file: nc.pull_file(f))  # Update files every 2 hours


def frontend():
    # Read Inventory File
    warehouses = []
    inventory = get_path(settings.data["path"])
    LOGGER.debug(f"Reading Data from {inventory}...")
    for sheet_num, sheet in enumerate(ezodf.opendoc(inventory).sheets):
        if sheet_num < settings.data["sheets"]:
            LOGGER.debug(f"Reading sheet {sheet.name}...")
            warehouses.append(Warehouse(name=sheet.name, inventory=read_ods(inventory, sheet_num + 1)))
    # Create default config
    create_default_config()
    # Ensure Filesystem Structure
    ensure_dirs([w.name for w in warehouses])
    # Read .md files
    markdown = get_markdown()
    # Manage env vars
    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    os.environ.setdefault("NICEGUI_STORAGE_PATH", str(get_path("users")))
    app.add_static_files('/images', str(get_path("images")))

    # Run
    ui.run(
        root=lambda: root(warehouses, markdown),
        language=settings.language,
        uvicorn_logging_level="debug" if ARGS.debug else "info",
        show=False,
        reload=ARGS.reload,
        uvicorn_reload_dirs=str(get_path("").parent.joinpath("src")),
        title=settings.title,
        favicon=get_path(settings.favicon),
        port=settings.port,
        storage_secret=storage_secret if storage_secret else '12341232312',
    )
    LOGGER.debug("Successfully started UI.")

if __name__ in {"__main__", "__mp_main__"}:
    #app.on_startup(backend)
    frontend()
