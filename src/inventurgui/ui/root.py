from nicegui import ui, app

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.safe_url import url_safe
from inventurgui.ui.helper.theme import Theme
from inventurgui.ui.layout import header, left_drawer, footer
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.finish import finish_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.sub_pages.login import login_page
from inventurgui.ui.sub_pages.start import start_page
from inventurgui.ui.sub_pages.warehouse import warehouse_page

"""The root page that constructs the layout and is only loaded on when requesting / ."""

def root(warehouses:list[Warehouse], markdown:dict[str, str]):
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
    ui.add_head_html(
        '<script src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.9.3/dist/dotlottie-wc.js" type="module"></script>')

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
            pages.add(f"/{name}/{url_safe(category)}", lambda w=warehouse, c=category: category_page(c, w, ld))
        if authenticate_user():
            pages.add(f"/{name}/{url_safe(i18n.get('admin.edits'))}", lambda w=warehouse, c=i18n.get('admin.edits'): category_page(c, w))

    header(ld)
    footer(ld)
