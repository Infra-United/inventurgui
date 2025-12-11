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
from inventurgui.io.request import Request
from inventurgui.ui.layout import header, right_drawer, footer
from inventurgui.ui.sub_pages import help_page, category_page, truck_page, form_page
from inventurgui.ui.theme import theme


def root():
    ui.add_head_html('''
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
    ''')

    LOGGER.setLevel(10) # DEBUG
    Nextcloud.inventory_path = config['data']['path']
    nc = Nextcloud()
    app.timer(7200, nc.update_inventory) # Update inventory_file every 2 hours
    app.storage.user.indent = True
    # Set colors and clear browser storage
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    # app.storage.clear()
    ui.query(".nicegui-content").classes("p-0 min-h-full lg:w-[calc(100dvw-250px)] max-lg:w-screen no-scroll sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)]") # remove default padding from site
    ui.query(".nicegui-sub-pages").classes('lg:w-[calc(100dvw-250px)] max-lg:w-screen scroll').style(replace='gap:0')
    app.storage.user['screen'] = 0 if not app.storage.user.get('screen') else app.storage.user['screen']
    app.storage.user['form'] =  Request() if not app.storage.user.get('form') else app.storage.user['form']
    app.storage.user['Total'] = 0 if not app.storage.user.get('Total') else app.storage.user['Total']
    app.storage.user['notified'] = {'truck': False} if not app.storage.user.get('notified') else app.storage.user['notified']
    ui.on('resize', lambda e: app.storage.user.update({'screen': e.args}), throttle=0.4, trailing_events=True)
    warehouses = nc.warehouses
    pages = ui.sub_pages(data={'warehouses': warehouses})
    pages.add('/', help_page)
    pages.add(f"/{url_safe(config['truck']['label'])}", truck_page)
    pages.add(f"/{url_safe(config['form']['label'])}", form_page)

    # Create Left Drawer
    ld = right_drawer(warehouses)

    #with ui.card().tight().classes('w-screen bg-black container overflow-auto p-0'):
    for warehouse in warehouses:
        app.storage.user[warehouse.name] = [] if not app.storage.user.get(warehouse.name) else app.storage.user[warehouse.name]
        warehouse = warehouse
        name = url_safe(warehouse.name)
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


def frontend():
    storage_secret = os.environ['UI_STORAGE_SECRET']
    ui.run(root=root, uvicorn_logging_level='debug', show=False, reload=True, title=config['title'], favicon=get_path(config['favicon']), port=8080, storage_secret=storage_secret if storage_secret else 12341232312)
    LOGGER.debug('Successfully started UI.')

if __name__ in {"__main__", "__mp_main__"}:
    frontend()


