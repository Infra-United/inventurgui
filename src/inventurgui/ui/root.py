from nicegui import ui, app
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.io.wiki import WikiChapter
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.theme import Theme
from inventurgui.ui.layout import header, left_drawer, footer, right_drawer
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.finish import finish_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.sub_pages.help import wiki_root, wiki_page
from inventurgui.ui.sub_pages.login import login_page
from inventurgui.ui.sub_pages.start import start_page

"""The root page that constructs the layout and is only loaded on when requesting / ."""

def root(warehouses:list[Warehouse], markdown:dict[str, str], wiki:dict[str, str | dict[str,str] |list[WikiChapter]]) -> None:
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
    ui.add_css(wiki.get("style"))
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
    rd = right_drawer(wiki.get('menu'))

    # Register Pages
    user_id = app.storage.browser["id"]
    pages = ui.sub_pages(data={"warehouses": warehouses, "ld": ld, "rd": rd, "user_id": user_id, "storage": storage, 'md':markdown}, show_404=False)
    pages.add("/", start_page)
    pages.add("/login", login_page)
    pages.add("/logout", login_page)
    pages.add(f"/{slugify(settings.cart['label'])}", cart_page)
    pages.add(f"/{slugify(settings.form['label'])}", form_page)
    pages.add(f"/{slugify(settings.finish['label'])}", finish_page)
    pages.add(f"/{slugify(settings.help['label'])}", wiki_root)

    # Register category sub_pages
    for warehouse in warehouses:
        warehouse = warehouse
        name = slugify(warehouse.name)
        for category in warehouse.categories:
            pages.add(f"/{name}/{slugify(category)}", lambda w=warehouse, c=category: category_page(c, w, ld))
        if authenticate_user():
            pages.add(f"/{name}/{slugify(i18n.get('admin.edits'))}", lambda w=warehouse, c=i18n.get('admin.edits'): category_page(c, w, ld))

    for chapter in wiki.get('menu'):
        pages.add(f"/{slugify(settings.help['label'])}/{slugify(chapter.name)}", wiki_page)

    header(ld)
    footer(ld)
