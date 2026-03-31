from bs4 import BeautifulSoup
from nicegui import ui
from nicegui.elements.drawer import LeftDrawer
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.images import generate_qrcode
from inventurgui.helper.logger import LOGGER
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

    async def share_content(verbose:bool = False) -> None:
        url = await ui.run_javascript('window.location.href')
        if not verbose:
            ui.clipboard.write(url)
            ui.notify(i18n.get("wiki.url_copied"), position='center', color='primary', textColor='secondary')
        soup = BeautifulSoup(content, 'html.parser')
        description = ""
        for i in soup.find_all(['p', 'span' 'em']):
            if desc := i.get_text(separator=" ", strip=True):
                description = desc.lstrip()[:400]
                break
        if verbose:
            ui.clipboard.write(f"{name.capitalize()}:\n\n{description} [...]\n\n{url}")
            ui.notify(i18n.get("wiki.info_copied"), position='center', color='primary', textColor='secondary')

    async def get_qr_code():
        url = await ui.run_javascript('window.location.href')
        qr, path = generate_qrcode(url, "wiki", name)
        with ui.dialog(value=True):
            with ui.image(qr.get_image()).classes("items-center"):
                ui.button("Download", icon='download').on('click', lambda: ui.download.file(path, slugify(name), "image/png")).props('active-icon=download')


    with ui.tab_panel(name).classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        if settings.help["wiki"]:
            html = ui.html(f"<head>{style}</head> {content}", sanitize=False)
            html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
            html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
            with ui.page_sticky(x_offset=40, y_offset=40):
                with ui.fab(icon='share', direction='up'):
                    ui.fab_action(icon='link').on('click', lambda: share_content()).props('active-icon=share')
                    ui.fab_action(icon='description').on('click', lambda: share_content(verbose=True)).props('active-icon=share')
                    ui.fab_action(icon='qr_code').on('click', get_qr_code).props('active-icon=share')
