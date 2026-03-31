
from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.io.cache import Cache
from inventurgui.ui.helper.markdown import render_markdown


async def help_page(ld: LeftDrawer, md: dict[str, str]):
    ld.hide()
    ui.page_title(f"{settings.help['label']}")
    LOGGER.debug(f"Creating help page...")
    with ui.tab_panel("help").classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        render_markdown(md.get(settings.help["label"]))

async def wiki_page(name: str, content: str, ld: LeftDrawer, style: str):
    ld.hide()
    ui.page_title(f"{name.capitalize()}")
    LOGGER.debug(f"Creating wiki page {name}...")

    def share_content():
        ui.run_javascript("""
        navigator.share({
                    title: document.title,
                    url: window.location.href,
                }).catch(console.error);
        """)

    with ui.tab_panel(name).classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        if settings.help["wiki"]:
            html = ui.html(f"<head>{style}</head> {content}", sanitize=False)
            html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
            html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
            if Cache.width() < 1024:
                with ui.page_sticky(x_offset=40, y_offset=40):
                    if Cache.share() is None:
                        ui.add_head_html(
                            """<script> emitEvent('share_check', {'is_allowed': navigator.share}); </script>""")
                        ui.on('share_check', lambda e: Cache.set_share(e.args['is_allowed']))
                    if Cache.share():
                        ui.fab(icon='share').on('click', share_content).props('active-icon=share')