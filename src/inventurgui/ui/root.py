from contextlib import suppress

from nicegui import ui, app
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.paths import ensure_directory_structure
from inventurgui.io.cache import Cache
from inventurgui.io.importer import read_ods
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse, WAREHOUSE_ROOT
from inventurgui.io.wiki import WIKI_ROOT, read_wiki, Wiki
from inventurgui.ui.helper.markdown import read_page_files
from inventurgui.ui.helper.theme import Theme
from inventurgui.ui.layout import create_layout
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.finish import finish_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.sub_pages.help import wiki_page, help_page
from inventurgui.ui.sub_pages.login import login_page
from inventurgui.ui.sub_pages.start import start_page

"""The root page that constructs the layout and is only loaded on when requesting / ."""


def root(
    warehouses: list[Warehouse],
    markdown: dict[str, str],
    wiki: Wiki = None,
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
    ui.on('resize', lambda e: Cache.set_width(e.args['width']), trailing_events=True, throttle=0.2)

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
    ui.timer(settings.refresh_timer, lambda: Nextcloud.singleton().pull_files(), immediate=False)
    ui.timer(settings.refresh_timer, lambda: (warehouses.clear(), warehouses.extend(read_ods())), immediate=False)
    ui.timer(settings.refresh_timer, lambda: ensure_directory_structure([w.name for w in warehouses]), immediate=False)
    ui.timer(settings.refresh_timer, lambda: markdown.update({k: v for k, v in read_page_files()}), immediate=False)
    ui.timer(settings.refresh_timer, lambda: wiki.update(read_wiki()) if display_wiki else None, immediate=False)

    # Instantiate Theme
    Theme.singleton().set_colors()

    # Set default styles
    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll h-[calc(100vh-56px)]")
    ui.query(".nicegui-sub-pages").classes("bg-dark w-full h-[calc(100vh-56px)] no-scroll").style(replace="gap:0")

    # init app storage
    storage = Cache(warehouses)

    # Create Main Layout
    ld, rd = create_layout(warehouses, wiki.menu if wiki else None)

    # Register Pages
    user_id = app.storage.browser["id"]
    sub_pages = ui.sub_pages(
        data={
            "warehouses": warehouses,
            "ld": ld,
            "rd": rd,
            "user_id": user_id,
            "storage": storage,
            "md": markdown,
            "style": wiki.style if wiki else None,
        },
        show_404=False,
    )
    sub_pages.add("/", start_page)
    sub_pages.add("/login", login_page)
    sub_pages.add("/logout", login_page)
    sub_pages.add(f"/{slugify(settings.cart['label'])}", cart_page)
    sub_pages.add(f"/{slugify(settings.form['label'])}", form_page)
    sub_pages.add(f"/{slugify(settings.finish['label'])}", finish_page)

    # Register category sub_pages
    sub_pages.add(f"/{WAREHOUSE_ROOT}", lambda: category_page(warehouses[0].name, warehouses[0], rd))
    for warehouse in warehouses:
        for category, route in warehouse.routes.items():
            sub_pages.add(route, lambda w=warehouse, c=category: category_page(c, w, rd))

    # Register help page    md_page =
    if not wiki:
        sub_pages.add(f"/{slugify(settings.help["label"])}", lambda: help_page(ld, markdown))
    else: # Register wiki pages
        sub_pages.add(f"/{WIKI_ROOT}", lambda: wiki_page(WIKI_ROOT, wiki.root, ld, wiki.style))
        for idx, chapter in enumerate(wiki.menu):
            with suppress(IndexError):
                pages = wiki.content[idx].pages
            for name, route in chapter.pages.items():
                page = pages.get(route.split('-')[-1])
                if not page:
                    continue
                sub_pages.add(route, lambda n=name, p=page: wiki_page(n, p, ld, wiki.style))
