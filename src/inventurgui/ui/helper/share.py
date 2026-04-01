from bs4 import BeautifulSoup
from nicegui import ui
from slugify import slugify

from inventurgui.helper.i18n import i18n
from inventurgui.helper.images import generate_qrcode


async def share_content(name:str, content:str, verbose: bool = False) -> None:
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


async def get_qr_code(name:str):
    url = await ui.run_javascript('window.location.href')
    qr, path = generate_qrcode(url, "wiki", name)
    with ((ui.dialog(value=True))):
        with ui.image(qr.get_image()).classes("items-center"):
            btn = ui.button("Download", icon='download')
            btn.on('click', lambda: ui.download.file(path, slugify(name), "image/png"))

