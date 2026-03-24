from nicegui import ui, app
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.paths import ensure_directory_structure
from inventurgui.io.cache import Cache
from inventurgui.io.importer import read_inventory
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse, WAREHOUSE_ROOT
from inventurgui.io.wiki import WikiChapter, WIKI_ROOT, pull_wiki, read_wiki
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.markdown import read_page_files
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


def root(
    warehouses: list[Warehouse],
    markdown: dict[str, str],
    wiki: None | dict[str, str | list[WikiChapter]] = None,
    display_wiki=None,
) -> None:
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
    ui.add_head_html(shared=True, code='<link rel="manifest" href="/helpers/manifest.json">')
    ui.add_head_html(shared=True, code='<script>if("serviceWorker" in navigator) { navigator.serviceWorker.register("/helpers/service_worker.js"); };</script>')
    ui.add_head_html(shared=True, code="""
    <!-- PWA Meta Tags generated with https://www.pwa-icon-generator.com/-->
        <link rel="icon" href="/favicon.ico" sizes="48x48">
        <link rel="icon" href="/icons/icon-192x192.png" type="image/png" sizes="192x192">
        <link rel="icon" href="/icons/icon-512x512.png" type="image/png" sizes="512x512">
        <link rel="apple-touch-icon" href="/icons/icon-180x180.png">
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#e89769">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="InfraUnited">
        
        <!-- iOS Splash Screens -->
        <!-- iPhone 16 Pro Max -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="/splash/splash-1290x2796.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)" href="/splash/splash-2796x1290.png">
        
        <!-- iPhone 16 Pro / 15 -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: portrait)" href="/splash/splash-1179x2556.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)" href="/splash/splash-2556x1179.png">
        
        <!-- iPhone SE / 8 -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="/splash/splash-750x1334.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)" href="/splash/splash-1334x750.png">
        
        <!-- iPad Pro 13" -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 1024px) and (device-height: 1366px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="/splash/splash-2048x2732.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 1024px) and (device-height: 1366px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)" href="/splash/splash-2732x2048.png">
        
        <!-- iPad Pro 11" -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="/splash/splash-1668x2388.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)" href="/splash/splash-2388x1668.png">
        
        <!-- iPad Air -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 820px) and (device-height: 1180px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="/splash/splash-1640x2360.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 820px) and (device-height: 1180px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)" href="/splash/splash-2360x1640.png">
        
        <!-- iPad Mini -->
        <link rel="apple-touch-startup-image" media="screen and (device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2) and (orientation: portrait)" href="/splash/splash-1536x2048.png">
        <link rel="apple-touch-startup-image" media="screen and (device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)" href="/splash/splash-2048x1536.png">

    """)


    # Set timers for refreshing files
    ui.timer(settings.refresh_timer, lambda: pull_wiki() if display_wiki else None, immediate=False)
    ui.timer(settings.refresh_timer, lambda: Nextcloud.singleton().pull_files(), immediate=False)
    ui.timer(settings.refresh_timer, lambda: (warehouses.clear(), warehouses.extend(read_inventory())), immediate=False)
    ui.timer(settings.refresh_timer, lambda: ensure_directory_structure([w.name for w in warehouses]), immediate=False)
    ui.timer(settings.refresh_timer, lambda: markdown.update({k: v for k, v in read_page_files()}), immediate=False)
    ui.timer(settings.refresh_timer, lambda: wiki.update(read_wiki()) if display_wiki else None, immediate=False)

    # Set colors
    Theme(settings.theme).set_colors()

    # Set default styles
    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll h-[calc(100vh-56px)]")
    ui.query(".nicegui-sub-pages").classes("bg-dark w-full h-[calc(100vh-56px)] no-scroll").style(replace="gap:0")

    # init app storage
    storage = Cache(warehouses)

    # Create Main Layout
    ld, rd = create_layout(warehouses, wiki.get("chapters") if wiki else None)

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
            "style": wiki.get("style") if wiki else None,
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
    pages.add(f"/{WAREHOUSE_ROOT}", lambda: category_page(warehouses[0].name, warehouses[0], rd))
    for warehouse in warehouses:
        warehouse = warehouse
        name = slugify(warehouse.name)
        for category in warehouse.categories:
            pages.add(
                f"/{WAREHOUSE_ROOT}/{name}/{slugify(category)}",
                lambda w=warehouse, c=category: category_page(c, w, rd),
            )
        if authenticate_user():
            pages.add(
                f"/{WAREHOUSE_ROOT}/{name}/{slugify(i18n.get('admin.edits'))}",
                lambda w=warehouse, c=i18n.get("admin.edits"): category_page(c, w, rd),
            )

    # Register wiki sub_pages
    md_page = markdown.get(settings.help["label"])
    if wiki:
        pages.add(f"/{WIKI_ROOT}", lambda: wiki_page(WIKI_ROOT, wiki.get("root"), ld, md_page, wiki.get("style")))
        for chapter in wiki.get("chapters"):
            pages.add(
                f"/{WIKI_ROOT}/{slugify(chapter.name)}",
                lambda c=chapter: wiki_page(c.name, c.pages.get(c.name), ld, md_page, wiki.get("style")),
            )
            for name, html in chapter.pages.items():
                pages.add(
                    f"/{WIKI_ROOT}/{slugify(chapter.name)}/{slugify(name)}",
                    lambda n=name, h=html: wiki_page(n, h, ld, md_page, wiki.get("style")),
                )
