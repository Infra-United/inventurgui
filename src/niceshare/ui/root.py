from nicegui import ui, app
from slugify import slugify

from niceshare.helper.config import settings
from niceshare.io.cache import Cache
from niceshare.io.selection import Selection, SELECTION_ROOT
from niceshare.ui.helper.theme import Theme
from niceshare.ui.layout import create_layout
from niceshare.ui.sub_pages.cart import cart_page
from niceshare.ui.sub_pages.category import category_page
from niceshare.ui.sub_pages.finish import finish_page
from niceshare.ui.sub_pages.form import form_page
from niceshare.ui.sub_pages.settings_page import settings_page
from niceshare.ui.sub_pages.start import start_page

"""The root page that constructs the layout and is only loaded on when requesting / ."""


def root(
    warehouses: list[Selection],
    markdown: dict[str, str],
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
    ui.on("resize", lambda e: Cache.set_width(e.args["width"]), trailing_events=True, throttle=0.2)

    ui.add_head_html(
        '<script src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.9.3/dist/dotlottie-wc.js" type="module"></script>'
    )
    ui.add_head_html(shared=True, code='<link rel="manifest" href="/helpers/manifest.json">')
    ui.add_head_html(
        shared=True,
        code='<script>if("serviceWorker" in navigator) { navigator.serviceWorker.register("/helpers/service_worker.js"); };</script>',
    )
    ui.add_head_html(
        shared=True,
        code="""
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

    """,
    )

    # Instantiate Theme
    Theme.singleton().set_colors()

    # Set default styles
    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll h-[calc(100vh-56px)]")
    ui.query(".nicegui-sub-pages").classes("bg-dark w-full h-[calc(100vh-56px)] no-scroll").style(replace="gap:0")

    # init app storage
    storage = Cache(warehouses)

    # Create Main Layout
    ld = create_layout(warehouses)

    # Register Pages
    user_id = app.storage.browser["id"]
    sub_pages = ui.sub_pages(
        data={
            "warehouses": warehouses,
            "ld": ld,
            "user_id": user_id,
            "storage": storage,
            "md": markdown,
        },
        show_404=False,
    )
    sub_pages.add("/", start_page)
    sub_pages.add(f"/{slugify(settings.cart['label'])}", cart_page)
    sub_pages.add(f"/{slugify(settings.form['label'])}", form_page)
    sub_pages.add(f"/{slugify(settings.finish['label'])}", finish_page)
    sub_pages.add(f"/{slugify('settings')}", settings_page)

    # Register category sub_pages
    sub_pages.add(f"/{SELECTION_ROOT}", lambda: category_page(warehouses[0].name, warehouses[0]))
    for warehouse in warehouses:
        for category, route in warehouse.routes.items():
            sub_pages.add(route, lambda w=warehouse, c=category: category_page(c, w))

