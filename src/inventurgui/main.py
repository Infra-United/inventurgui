import asyncio
import random
import string

from nicegui import ui

from inventurgui.helper.config import config, theme, get_path
# from ui.admin import admin
# from ui.auth import try_login
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
from inventurgui.ui.sub_pages import SubPage


def root():
    # Set colors and clear browser storage
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    # app.storage.clear()

    pages = ui.sub_pages()
    sub_page = SubPage()

    ui.query('.nicegui-content').classes('p-0') # remove default padding from site

    # Create Header
    with ui.header().classes('p-0 m-0 h-50px bg-secondary text-primary') as header:
        for key, label in sub_page.pages.items():
            if key == 'help': # Register as Start Page
                ui.button(icon='help_outline', on_click=lambda l=label: ui.navigate.to(f"/"))
            else:
                ui.button(label, on_click=lambda l=url_safe(label): ui.navigate.to(f"/{l}"))

    # Create Sub Pages
    with ui.card().tight().classes('w-screen bg-black container overflow-auto p-0'):
        for key, label in sub_page.pages.items():
            label = url_safe(label)
            match key:
                case 'help':
                    pages.add(f"/{label}", sub_page.help)
                case 'everything':
                    pages.add(f"/{label}", sub_page.everything)
                case _:
                    pages.add(f"/{label}", lambda k=key: sub_page.category(k))


                  #  with ui.card().classes('m-0 h-dvh content-center bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                  #      with ui.card().classes(''):
                #            username = ui.input('Username').value
                 #           password = ui.input('Password', password=True, password_toggle_button=True).value
                          #  ui.button('Log in/Register', on_click=try_login(username, hash_password(password)))

    LOGGER.debug('Finished. Starting UI...')

async def main():
    LOGGER.setLevel(10) # DEBUG
    Nextcloud.data_path = config['data']['path']
    nc = Nextcloud()
    await nc.__post_init__()

    SubPage.nc = nc
    SubPage.help_path = get_path(config['help']['path'])
    SubPage.pages = {}
    if config['help']['display']:
        SubPage.pages['help'] = config['help']['label']
    if config['everything']['display']:
        SubPage.pages['everything'] = config['everything']['label']

    categories: list[str] = sorted(nc.data[config['data']['category']].unique())
    for category in categories:
        SubPage.pages[category] = category

def start_ui():
    storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
    ui.run(root=root, uvicorn_logging_level='debug', show=False, reload=True, title=config['title'], favicon=get_path(config['favicon']), port=8080, storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')

if __name__ in {"__main__", "__mp_main__"}:
    asyncio.run(main())
    start_ui()


