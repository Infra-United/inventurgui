from bs4 import BeautifulSoup
from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
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

    async def share_content() -> None:
        if Cache.share():
            await ui.run_javascript("""
            navigator.share({
                        title: document.title,
                        url: window.location.href,
                    }).catch(console.error);
            """)
        else:
            url = await ui.run_javascript('window.location.href')
            soup = BeautifulSoup(content, 'html.parser')
            description = ""
            for i in soup.find_all(['p', 'span' 'em']):
                if desc := i.get_text(separator=" ", strip=True):
                    description = desc.lstrip()[:400]
                    break
            ui.clipboard.write(f"{name.capitalize()}:\n\n{description} [...]\n\n{url}")
            ui.notify(i18n.get("wiki.url_copied"), position='center', color='primary', textColor='secondary')

    with ui.tab_panel(name).classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        if settings.help["wiki"]:
            html = ui.html(f"<head>{style}</head> {content}", sanitize=False)
            html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
            html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
            with ui.page_sticky(x_offset=40, y_offset=40):
                if Cache.share() is None:
                    ui.add_head_html(
                        """<script> emitEvent('share_check', {'is_allowed': navigator.share}); </script>""")
                    ui.on('share_check', lambda e: Cache.set_share(True if e.args['is_allowed'] == 'true' else False))
                ui.fab(icon='share').on('click', share_content).props('active-icon=share')
