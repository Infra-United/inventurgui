import os
from os import mkdir

import ezodf
from nicegui import ui, app
from pandas_ods_reader import read_ods

from inventurgui.cli import ARGS
from inventurgui.helper.config import config, get_path, load_config
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
# from ui.admin import admin
# from ui.auth import try_login
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import header, left_drawer, footer
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.finish import finish_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.sub_pages.start import start_page
from inventurgui.ui.sub_pages.warehouse import warehouse_page
from inventurgui.ui.theme import Theme


def root():
    # Everytime a user loads the page this is executed - creates the layout - content is created by sub_pages.


    ui.add_head_html('''
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
    ''')

    warehouses = []
    inventory = get_path(config['data']['path'])
    LOGGER.debug(f"Reading Data from {inventory}...")
    for sheet_num, sheet in enumerate(ezodf.opendoc(inventory).sheets):
        if sheet_num < config['data']['sheets']:
            LOGGER.debug(f"Reading sheet {sheet.name}...")
            warehouses.append(Warehouse(name=sheet.name, inventory=read_ods(inventory, sheet_num + 1)))

    # Set colors
    t = (Theme(load_config()['theme']).set_colors())

    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll h-[calc(100vh-56px)]") # remove default padding from site
    ui.query(".nicegui-sub-pages").classes('bg-dark w-full h-[calc(100vh-56px)] no-scroll').style(replace='gap:0')
    ui.on('resize', lambda e: app.storage.user.update({'screen': e.args}), throttle=0.4, trailing_events=True)

    # init app storage
    app.storage.user.indent = True
    app.storage.user.setdefault('screen', {})
    app.storage.user.setdefault('notified', {'selection': False})
    app.storage.user.setdefault('Total', 0)
    app.storage.user.setdefault('form', {"dates": None, "name": "", "place": "", "donation": "",
                                         "email": "", "message": "", "sent": None})
    app.storage.user.setdefault('amounts', {})

    # Create Left Drawer
    ld = left_drawer(warehouses)

    # Register Pages
    user_id = app.storage.browser['id']
    pages = ui.sub_pages(data={'warehouses': warehouses, 'ld': ld, 'user_id': user_id})
    pages.add(f"/", start_page)
    pages.add(f"/{url_safe(config['warehouse']['label'])}", warehouse_page)
    pages.add(f"/{url_safe(config['cart']['label'])}", cart_page)
    pages.add(f"/{url_safe(config['form']['label'])}", form_page)
    pages.add(f"/{url_safe(config['finish']['label'])}", finish_page)

    # Register categories
    amounts = app.storage.user['amounts']
    for warehouse in warehouses:
        app.storage.user.setdefault(warehouse.name, [])
        amounts.update({warehouse.name: {}}) if not amounts.get(warehouse.name) else None
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

def backend():
    nc = Nextcloud.singleton()
    for key, file in config['cloud']['pull'].items():
       app.timer(7200, lambda f=file: nc.update_file(f)) # Update files every 2 hours

def frontend():
    storage_secret = os.environ['UI_STORAGE_SECRET']
    user_dir = get_path('users')
    if not user_dir.exists():
        mkdir(user_dir)
    os.environ.setdefault('NICEGUI_STORAGE_PATH', str(user_dir))
    ui.run(root=root, language=config['language'], uvicorn_logging_level='debug' if ARGS.debug else 'info', show=False, reload=ARGS.debug, title=config['title'], favicon=get_path(config['favicon']), port=8080, storage_secret=storage_secret if storage_secret else 12341232312)
    LOGGER.debug('Successfully started UI.')

if __name__ in {"__main__", "__mp_main__"}:
    app.on_startup(backend)
    frontend()


