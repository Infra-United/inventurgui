import random
import string

from nicegui import ui, app

from inventurgui.helper.config import config, theme, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
# from ui.admin import admin
# from ui.auth import try_login
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.ui.layout import header, left_drawer, footer
from inventurgui.ui.sub_pages import help_page, warehouse_page, category_page


def root():
    LOGGER.setLevel(10) # DEBUG
    Nextcloud.inventory_path = config['data']['path']
    nc = Nextcloud()
    app.timer(3600, nc.update_inventory) # Update inventory_file every hour

    # Set colors and clear browser storage
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    # app.storage.clear()
    ui.query(".nicegui-content").classes("p-0 min-h-full w-screen no-scroll sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)]") # remove default padding from site

    warehouses = nc.warehouses
    pages = ui.sub_pages(data={'warehouses': warehouses})
    pages.add('/', help_page)

    # Create Left Drawer
    ld = left_drawer()

    #with ui.card().tight().classes('w-screen bg-black container overflow-auto p-0'):
    for warehouse in warehouses:
        warehouse = warehouse
        name = url_safe(warehouse['name'])
        pages.add(f'/{name}', lambda w=warehouse: warehouse_page(w, ld))
        categories = sorted(warehouse['inventory'][config['data']['category']].unique())
        if len(categories) > 1:
            everything = url_safe(config['everything']['label'])
            pages.add(f'/{name}/{everything}', lambda w=warehouse: warehouse_page(w, ld))
        for category in categories:
            pages.add(f'/{name}/{url_safe(category)}', lambda i=warehouse['inventory'], c=category: category_page(c, i))




    header(warehouses, ld)
    footer(warehouses, ld)
    """
    # Create Sub Pages
    with ui.card().tight().classes('w-screen bg-black container overflow-auto p-0'):
        for key, label in sub_page.pages.items():
            label = url_safe(label)
            match key:
                case 'help':
                    pages.add(f"/{label}", sub_page.help)
                case 'everything':
                    pages.add(f"/{label}", sub_page.warehouse)
                case _:
                    pages.add(f"/{label}", lambda k=key: sub_page.category(k))
"""

                  #  with ui.card().classes('m-0 h-dvh content-center bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                  #      with ui.card().classes(''):
                #            username = ui.input('Username').value
                 #           password = ui.input('Password', password=True, password_toggle_button=True).value
                          #  ui.button('Log in/Register', on_click=try_login(username, hash_password(password)))

    LOGGER.debug('Finished. Starting UI...')

#async def backend():

def frontend():
    storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
    ui.run(root=root, uvicorn_logging_level='debug', show=False, reload=True, title=config['title'], favicon=get_path(config['favicon']), port=8080, storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')

if __name__ in {"__main__", "__mp_main__"}:
    #asyncio.run(backend())
    frontend()


