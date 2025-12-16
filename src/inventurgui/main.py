import os

import ezodf
from nicegui import ui, app
from nicegui.elements.drawer import LeftDrawer
from pandas_ods_reader import read_ods

from inventurgui.helper.config import config, get_path, theme, start
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
# from ui.admin import admin
# from ui.auth import try_login
from inventurgui.io.nextcloud import Nextcloud
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import header, left_drawer, footer, tabs, tab_panels
from inventurgui.ui.markdown import render_markdown
from inventurgui.ui.sub_pages.cart import cart_page
from inventurgui.ui.sub_pages.category import category_page
from inventurgui.ui.sub_pages.form import form_page
from inventurgui.ui.theme import Theme


async def main_page(ld:LeftDrawer) -> None:
    # Create one Page for displaying help
    ld.hide()
    main_tabs = tabs()
    main_panels = tab_panels(main_tabs)
    for key, values in start.items():
        if not values['display']:
            continue
        with main_tabs:
            label = values.get('label')
            ui.tab(label, icon=values.get('icon')).classes('px-7').props('inline-label')
        with main_panels:
            with ui.tab_panel(label).classes('m-0 p-0'):
                await render_markdown(values)
    main_panels.set_value([t.props.get('label') for t in main_tabs.descendants()][0]) # First tab is open by default

def root():
    LOGGER.setLevel(10)  # DEBUG
    nc = Nextcloud(remote_dir=config['cloud']['dir'])
    for key, file in config['cloud']['pull'].items():
        app.timer(7200, lambda f=file: nc.update_file(f))  # Update files every 2 hours

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
    t = (Theme(theme).set_colors())
    ui.dark_mode(theme.get('dark_mode'), on_change=lambda e: t.toggle_dark(e.value))
    ui.query(".nicegui-content").classes("p-0 min-h-full bg-dark w-full no-scroll sm:h-[calc(100vh-56px)] h-[calc(100vh-52px)]") # remove default padding from site
    ui.query(".nicegui-sub-pages").classes(' bg-dark w-full scroll').style(replace='gap:0')
    ui.on('resize', lambda e: app.storage.user.update({'screen': e.args}), throttle=0.4, trailing_events=True)

    # init app storage
    app.storage.user.indent = True
    app.storage.user['screen'] = 0 if not app.storage.user.get('screen') else app.storage.user['screen']
    app.storage.user['form'] = {} if not app.storage.user.get('form') else app.storage.user['form']
    app.storage.user['Total'] = 0 if not app.storage.user.get('Total') else app.storage.user['Total']
    app.storage.user['amounts'] = {} if not app.storage.user.get('amounts') else app.storage.user['amounts']
    app.storage.user['notified'] = {'selection': False} if not app.storage.user.get('notified') else app.storage.user[
        'notified']


    # Create Left Drawer
    ld = left_drawer(warehouses)

    # Register Pages
    pages = ui.sub_pages(data={'warehouses': warehouses, 'ld': ld})
    pages.add(f"/", main_page)
    pages.add(f"/{url_safe(config['cart']['label'])}", cart_page)
    pages.add(f"/{url_safe(config['request']['label'])}", form_page)

    for warehouse in warehouses:
        app.storage.user[warehouse.name] = [] if not app.storage.user.get(warehouse.name) else app.storage.user[warehouse.name]
        app.storage.user['amounts'][warehouse.name] = {} if not app.storage.user['amounts'].get(warehouse.name) else app.storage.user['amounts'][warehouse.name]
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
    ui.run(root=root, language=config['language'], uvicorn_logging_level='debug', show=False, reload=True, title=config['title'], favicon=get_path(config['favicon']), port=8080, storage_secret=storage_secret if storage_secret else 12341232312)
    LOGGER.debug('Successfully started UI.')

if __name__ in {"__main__", "__mp_main__"}:
    frontend()


