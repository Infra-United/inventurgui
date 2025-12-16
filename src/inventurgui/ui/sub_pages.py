import datetime
import re
from contextlib import suppress
from typing import Literal

import requests
from nicegui import ui, app, run
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.button import Button
from nicegui.elements.drawer import LeftDrawer
from nicegui.elements.markdown import Markdown
from nicegui.elements.tabs import Tabs
from requests import ReadTimeout

from inventurgui.helper.config import config, get_path, EMAIL_REGEX, start, request_conf
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.mail import Mail
from inventurgui.io.request import Request
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import checkout_fab, back_fab


def tabs():
    return ui.tabs().classes('bg-secondary h-[56px] w-full scroll font-bold subpixel-antialiased tracking-widest m-0 p-0').props(
        'height=56px active-bg-color=accent inline-label mobile-arrows stretch')

def tab_panels(tabs:Tabs):
    return ui.tab_panels(tabs).classes('w-full h-dvh')

async def cart_page(ld:LeftDrawer, warehouses:list[Warehouse]) -> None:
    total = app.storage.user.get('Total', 0)
    if total == 0:
        ui.notify(config['cart']['select_tip'], position='center', color='primary', textColor='dark')
        ui.navigate.to('/')
        return
    if not app.storage.user.get('notified')['selection'] and total != 0:
        ui.notify(config['cart']['edit_tip'], position='center', color='primary', textColor='dark')
        app.storage.user['notified']['selection'] = True
    ld.hide()
    truck_tabs = tabs()
    truck_panels = tab_panels(truck_tabs)
    LOGGER.debug(f'Creating Cart page...')
    for w in warehouses:
        selected = await w.selected()
        if selected is None or selected.empty:
            continue
        with truck_tabs:
            with ui.tab(w.name.upper(), icon=config['cart']['icon']).classes('px-7').props('inline-label'):
                badge = ui.badge('0', color='accent').props("floating").classes('text-bold')
                badge.bind_text_from(app.storage.user, w.name, lambda e: len(e))
        with truck_panels:
            with ui.tab_panel(w.name.upper()).classes('m-0 p-0 w-full'):
                grid: AgGrid = create_aggrid(w.name, selected, config, cart=True)
    truck_panels.set_value(warehouses[0].name.upper())
    LOGGER.info(f"Created cart page")
    checkout_fab(request_conf)

async def form_page(ld:LeftDrawer, warehouses:list[Warehouse]) -> None:
    ld.hide()
    def parse_date(v:dict, t:Literal['from', 'to']) -> datetime.date|None:
        with suppress(AttributeError):
            return v.get(t, None)
        return None

    def validate_form() -> bool:
        checks = [name.validate(),
                  place.validate(),
                  email.validate(),
                  dates.value,
                  donation.validate(),
                  check.value,
                  app.storage.user.get('Total') == 0
                  ]
        with suppress(NameError):
            if any(checks):
                return False
        return True

    def handle_submit():
        if not validate_form():
            ui.notify('Please fill out the form correctly.')
            return
        request = Request.from_dict(bind)
        #Mail.send_mail(request.html(message.value), request.subject, request.email)
        request.write_ods(warehouses)

    today = datetime.date.today()
    form = request_conf.get('form')
    terms = request_conf.get('terms')
    bind = app.storage.user.get('form')
    form_tabs = tabs()
    form_panels = tab_panels(form_tabs)
    back_fab(config['cart'])
    with form_tabs:
        with form_tabs:
            ui.tab(form.get('label'), icon=form.get('icon')).classes('px-7').props('inline-label')
            ui.tab(terms.get('label'), icon=terms.get('icon')).props('inline-label')
        with form_panels:
            with ui.tab_panel(form.get('label')).classes('m-0'):
                with ui.grid(columns=1).classes('xl:w-1/2 w-full bg-dark h-screen lg:w-1/2'):
                    name = ui.input(form.get('name'), validation={form.get('please_fill'): lambda v: len(v) > 0})
                    name.bind_value(bind, 'name').props('debounce=1000')
                    place = ui.input(form.get('place'), validation={form.get('please_fill'): lambda v: len(v) > 0})
                    place.bind_value(bind, 'place').props('debounce=1000')
                    email = ui.input(form.get('email'),validation={form.get('email_invalid'): lambda v: True if re.match(EMAIL_REGEX, v) else False})
                    email.bind_value(bind, 'email').props('debounce=1000')
                    ui.label(f"{form.get('start')} - {form.get('end')}".upper()).classes('w-full pt-2 text-center tracking-widest')
                    dates = ui.date().classes('w-100 p-0 mx-auto').props('range minimal flat')
                    dates.props[':options'] = f'date => date >= "{today:%Y/%m/%d}"'
                    dates.bind_value_to(bind, 'start', forward=lambda v: parse_date(v, 'from'))
                    dates.bind_value_to(bind, 'end', forward=lambda v: parse_date(v, 'to'))
                    message = ui.editor(placeholder=form.get('message'))
                    donation = ui.input(form.get('donation'), validation={form.get('please_fill'): lambda v: len(v) > 0})
                    donation.bind_value(bind, 'donation').props('debounce=1000')
                    check = ui.checkbox(form.get('checkbox'))
                    with ui.row().classes('pb-10'):
                        ui.space()
                        submit = ui.button(form.get('submit')).props('text-color=secondary rounded icon-right=send')
                        correct = validate_form()
                        submit.bind_enabled_from(correct) #TODO FIX submit enabled
                        submit.classes('p-3 sm:w-80 text-lg')
                    submit.on_click(lambda: handle_submit())
            with ui.tab_panel(terms.get('label')).classes('m-0 p-0'):
                await render_markdown(request_conf.get('terms'))
    form_panels.set_value([t.props.get('label') for t in form_tabs.descendants()][0]) # First tab is open by default


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

def category_page(category:str, warehouse: Warehouse) -> None:
    # Create One grid for each unique Category in the first Column
    LOGGER.debug(f'Creating Grid for {warehouse.name}/{category}...')
    category_data = warehouse.inventory[warehouse.inventory[config['data']['category']] == category]
    if category == config['everything']:
        category_data = warehouse.inventory
    grid:AgGrid = create_aggrid(warehouse.name, category_data, config)
    checkout_fab(config['cart'])
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")

async def render_markdown(values:dict[str, str]) -> Markdown:
    label = values.get('label')
    path = get_path(values.get('path'))
    try:
        with open(path, 'r') as f:  # open file
            LOGGER.debug(f"Creating {label} with the content of {path}...")
            text = f.read()
    except FileNotFoundError:
        if url := values.get('url'):
            LOGGER.debug(f"Getting {label} content from {url}...")
            try:
                response = await run.io_bound(lambda: requests.get(url, timeout=2))
                print(response)
                with open(path, 'w') as f:
                    f.write(response.text)
                LOGGER.info(f"Successfully fetched {label} content from {url}!")
            except ReadTimeout as e:
                text = (f"<br>The URL: [{url}]({url}) for page: **{label}** could not be fetched."
                 f"<br><br>Please check your Internet Connection, the url and try opening it manually.")
        else:
            text = (f"<br>path:{path.name}<br> in config for page **{label}** does not exist."
                    f"<br>Please review your config, read the logs and check /files."
                    f"<br>If you started the program for the first time i may have fetched the page by now."
                    f"<br>In that case a page reload might also fix the problem.")
    return ui.markdown(text).classes('p-10 pt-5 mx-auto text-pretty text-base/8 text-gray-300 max-w-[740px]')