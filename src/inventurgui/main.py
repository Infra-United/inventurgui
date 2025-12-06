import os
import random
import string

from nicegui import ui, app

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
# from ui.admin import admin
# from ui.auth import try_login
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.ui.layout import header, left_drawer, footer
from inventurgui.ui.sub_pages import help_page, warehouse_page, category_page
from inventurgui.ui.theme import theme


def root():
    LOGGER.setLevel(10) # DEBUG
    Nextcloud.inventory_path = config['data']['path']
    nc = Nextcloud()
    app.timer(7200, nc.update_inventory) # Update inventory_file every 2 hours
    app.storage.user.indent = True
    # Set colors and clear browser storage
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    # app.storage.clear()
    ui.query(".nicegui-content").classes("p-0 min-h-full w-screen no-scroll sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)]") # remove default padding from site

    warehouses = nc.warehouses
    pages = ui.sub_pages(data={'warehouses': warehouses})
    pages.add('/', help_page)

    # Create Left Drawer
    ld = left_drawer(warehouses)

    #with ui.card().tight().classes('w-screen bg-black container overflow-auto p-0'):
    for warehouse in warehouses:
        app.storage.user[warehouse.name] = [] if not app.storage.user.get(warehouse.name) else app.storage.user[warehouse.name]
        warehouse = warehouse
        name = url_safe(warehouse.name)
        pages.add(f'/{name}', lambda w=warehouse: warehouse_page(w))
        for category in warehouse.categories:
            pages.add(f'/{name}/{url_safe(category)}', lambda w=warehouse, c=category: category_page(c, w))




    header(ld)
    footer(ld)

  #  with ui.card().classes('m-0 h-dvh content-center bg-black text-base anitaliased font-light text-secondary decoration-primary'):
  #      with ui.card().classes(''):
#            username = ui.input('Username').value
 #           password = ui.input('Password', password=True, password_toggle_button=True).value
          #  ui.button('Log in/Register', on_click=try_login(username, hash_password(password)))

    LOGGER.debug('Finished. Starting UI...')

#async def backend():

def frontend():
    storage_secret = os.environ['UI_STORAGE_SECRET']
    ui.run(root=root, uvicorn_logging_level='debug', show=False, reload=True, title=config['title'], favicon=get_path(config['favicon']), port=8080, storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')

if __name__ in {"__main__", "__mp_main__"}:
    #asyncio.run(backend())
    frontend()


