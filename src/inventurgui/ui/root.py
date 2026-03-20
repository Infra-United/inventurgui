from nicegui import ui, app
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse, WAREHOUSE_ROOT
from inventurgui.io.wiki import WikiChapter, WIKI_ROOT
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.theme import Theme
from inventurgui.ui.layout import create_layout
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.finish import finish_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.sub_pages.help import wiki_page
from inventurgui.ui.sub_pages.login import login_page
from inventurgui.ui.sub_pages.start import start_page

"""The root page that constructs the layout and is only loaded on when requesting / ."""


def root(warehouses: list[Warehouse], markdown: dict[str, str], wiki: dict[str, str | list[WikiChapter]]) -> None:
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
        '<script src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.9.3/dist/dotlottie-wc.js" type="module"></script>'
    )

    # Set colors
    Theme(settings.theme).set_colors()

    # Set default styles
    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll h-[calc(100vh-56px)]")
    ui.query(".nicegui-sub-pages").classes("bg-dark w-full h-[calc(100vh-56px)] no-scroll").style(replace="gap:0")

    # init app storage
    storage = Cache(warehouses)

    # Create Main Layout
    ld, rd = create_layout(warehouses, wiki.get("chapters"))

    # Register Pages
    user_id = app.storage.browser["id"]
    pages = ui.sub_pages(
        data={
            "warehouses": warehouses,
            "ld": ld,
            "rd": rd,
            "user_id": user_id,
            "storage": storage,
            "md": markdown,
            "style": wiki.get("style"),
        },
        show_404=False,
    )
    pages.add("/", start_page)
    pages.add("/login", login_page)
    pages.add("/logout", login_page)
    pages.add(f"/{slugify(settings.cart['label'])}", cart_page)
    pages.add(f"/{slugify(settings.form['label'])}", form_page)
    pages.add(f"/{slugify(settings.finish['label'])}", finish_page)

    # Register category sub_pages
    pages.add(f"/{WAREHOUSE_ROOT}", lambda: category_page(warehouses[0].name, warehouses[0], ld, rd))
    for warehouse in warehouses:
        warehouse = warehouse
        name = slugify(warehouse.name)
        for category in warehouse.categories:
            pages.add(
                f"/{WAREHOUSE_ROOT}/{name}/{slugify(category)}",
                lambda w=warehouse, c=category: category_page(c, w, ld, rd),
            )
        if authenticate_user():
            pages.add(
                f"/{WAREHOUSE_ROOT}/{name}/{slugify(i18n.get('admin.edits'))}",
                lambda w=warehouse, c=i18n.get("admin.edits"): category_page(c, w, ld, rd),
            )

    # Register wiki sub_pages
    pages.add(f"/{WIKI_ROOT}", lambda: wiki_page(WIKI_ROOT, wiki.get("root"), ld, rd, wiki.get("style")))
    for chapter in wiki.get("chapters"):
        pages.add(
            f"/{WIKI_ROOT}/{slugify(chapter.name)}",
            lambda c=chapter: wiki_page(c.name, c.pages.get(c.name), ld, rd, wiki.get("style")),
        )
        for name, html in chapter.pages.items():
            pages.add(
                f"/{WIKI_ROOT}/{slugify(chapter.name)}/{slugify(name)}",
                lambda n=name, h=html: wiki_page(n, h, ld, rd, wiki.get("style")),
            )
