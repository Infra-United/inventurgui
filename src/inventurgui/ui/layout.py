from nicegui import ui, app
from nicegui.elements.button import Button
from nicegui.elements.drawer import LeftDrawer
from nicegui.elements.tabs import Tabs

from inventurgui.helper.config import config, menu, get_path
from inventurgui.helper.safe_url import url_safe, reverse_url
from inventurgui.io.warehouse import Warehouse

menu_buttons:dict[str, Button] = {}

def handle_path_change(warehouse:bool=False):
    def invert_button(btn:Button):
        [(b.classes(remove='bg-accent'), b.props.update({'text-color': 'secondary'})) for b in menu_buttons.values()]
        btn.classes(add='bg-accent').props.update({'text-color': 'white'})
        btn.update()
    path = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-1])
    if warehouse:
        invert_button(menu_buttons.get(url_safe(menu['warehouse']['label'])))
        ui.notify(menu_buttons.get(url_safe(menu['warehouse']['label'])).classes)
        return True
    if ui.context.client.sub_pages_router.current_path == "/":
        invert_button(menu_buttons.get(url_safe(menu['start']['label'])))
        return True
    for label, btn in menu_buttons.items():
        invert_button(btn) if label == path else None
        return True
    return [(b.classes(remove='bg-accent'), b.props.update({'text-color': 'secondary'})) for b in menu_buttons.values()]


def main_menu(ld:LeftDrawer, classes:str="stretch", props:str="unelevated no-wrap text-color=secondary square") -> dict[str, Button]:
    global menu_buttons
    for key, values in menu.items():
        btn:Button = ui.button(values.get('label'), icon=values.get('icon')).classes(classes).props(props)
        if key == 'start':
            btn.on_click(lambda l=url_safe(values['label']): ui.navigate.to(f"/"))
            ui.on('resize', lambda b=btn: b.move(target_index=1) if app.storage.user.get('screen')['width'] < 1024 else b.move(target_index=3) , throttle=0.8, trailing_events=True)
            ui.space().classes('max-sm:hidden')
        elif key == 'warehouse':
            btn.classes(classes).on_click(lambda: ld.toggle())
        else:
            btn.on_click(lambda l=url_safe(values['label']): ui.navigate.to(f"/{l}"))
        if not key == 'warehouse':
            btn.on_click(
                lambda: [(b.classes(remove='bg-accent'), b.props.update({'text-color': 'secondary'})) for b in menu_buttons.values()])
            btn.on_click((lambda b=btn: b.classes(add='bg-accent').props.update({'text-color': 'white'})))
        menu_buttons.update({url_safe(values['label']): btn})
    handle_path_change()
    return menu_buttons


def warehouse_menu(warehouses:list[Warehouse], ld:LeftDrawer, classes:str, props:str):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    path_category = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-1])
    path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-2])

    with ui.row().classes('flex bg-primary row w-full px-20 py-3 mb-1'):
        ui.icon(config['menu']['warehouse']['icon'], size='20px', color='secondary').classes(classes)
        ui.label(config['menu']['warehouse']['label'].upper()).classes(classes).classes('text-secondary')
    for warehouse in warehouses:
        name = warehouse.name
        with ui.expansion(group='menu').classes(classes) as expansion:
            expansion.props(f"{props} header-class='bg-secondary' hide-expand-icon")
            expansion.on_value_change(lambda v, e=expansion: e.props.update(
                {"header-class": 'bg-accent'} if v.value else {
                    "header-class": 'bg-secondary'}))
            expansion.set_value(True if name == path_warehouse else True if name == warehouses[0].name else False)
            expansion.on('click', lambda l=url_safe(name): ui.navigate.to(f"/{l}/{url_safe(config['everything'])}"))
            expansion.on('click', lambda e=expansion: e.open())
            expansion.on('click', lambda: handle_path_change(warehouse=True))
            with expansion.add_slot('header'):
                with ui.label(name.upper()).classes('py-3 w-full'):
                    badge = ui.badge('0', color='secondary').props("floating").classes('text-bold')
                    badge.bind_text_from(app.storage.user, warehouse.name, backward=lambda v:str(len(v)), strict=False)
            if len(warehouse.categories) == 2:
                expansion.on('click', lambda: (ld.hide()) if app.storage.user.get('screen')['width'] < 1024 else None)
                continue
            toggle = ui.toggle(warehouse.categories)
            toggle.set_value(path_category)
            toggle.classes(f"{classes} column").props('square unelevated stretch toggle-color=accent')
            toggle.on_value_change(lambda v, w=warehouse: ui.navigate.to(f"/{url_safe(w.name)}/{url_safe(v.value)}"))
            toggle.on_value_change(lambda: handle_path_change(warehouse=True))
            toggle.on_value_change(lambda: ld.hide() if app.storage.user.get('screen')['width'] < 1024 else None)


def header(ld:LeftDrawer):
    with ui.header().classes("fixed max-sm:hidden h-[56px] bg-primary flex-nowrap m-0 pr-3 p-0 items-center"):
        ui.image(source=get_path(config.get('favicon'))).classes('h-full m-0 p-0 w-[56px]')
        ui.label(str(config.get('title')).upper()).classes('text-secondary w-[161px] max-lg:hidden text-bold text-xl')
        main_menu(ld, classes='stretch h-full')

def footer(ld:LeftDrawer):
    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden p-0 gap-0 h-[52px]"):
        main_menu(ld,
            props='label="" unelevated no-wrap text-color=dark square',
            classes="flex-auto stretch h-full",
        )

def left_drawer(warehouses:list[Warehouse]) -> LeftDrawer:
    with ui.left_drawer(bordered=True).classes("gap-0 p-0 items-stretch").props('width=250') as ld:
        classes: str = "text-center text-gray-200 py-1 m-0 font-bold subpixel-antialiased tracking-widest"
        props: str = "unelevated square"
        ui.space().classes("sm:hidden")
        warehouse_menu(warehouses, ld, classes, props)
    return ld

def checkout_fab(next_page:dict[str, str]):
    props: str = f"text-color=secondary"
    with (ui.page_sticky(position='bottom-right', x_offset=18, y_offset=18).classes('z-999')):
        #TODO Tooltip
        #ui.tooltip("Hier findest du ein paar Werkzeuge.").props('left')
        fab = ui.fab(icon='navigate_next', direction='up').props(f"{props}")
        fab.on('click', lambda: ui.navigate.to(url_safe(f"/{next_page.get('label')}")) if badge.visible else None)
        fab.on('click', lambda: handle_path_change(warehouse=False))
        fab.bind_visibility_from(app.storage.user, 'Total', backward=lambda v: v>0)
        fab.on('mouseenter', lambda: label.set_visibility(True), throttle=0.2)
        fab.on('mouseleave', lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot('label'):
            with ui.row():
                icon = ui.icon(next_page.get('icon'))
                label = ui.label(next_page.get('label')).classes('text-secondary text-base')
                label.set_visibility(False)
            badge = ui.badge('0', color='primary', text_color='secondary').props(
                "rounded floating").classes('text-bold')
            badge.bind_text_from(app.storage.user, 'Total')
            badge.bind_visibility_from(app.storage.user, 'Total', backward=lambda v: v>0)

def back_fab(last_page:dict[str, str]):
    props: str = f"text-color=secondary"
    with (ui.page_sticky(position='bottom-left', x_offset=18, y_offset=18).classes('z-999')):
        # TODO Tooltip
        # ui.tooltip("Hier findest du ein paar Werkzeuge.").props('left')
        fab = ui.fab(icon='navigate_before', direction='up').props(f"{props}")
        fab.on('click', lambda: ui.navigate.to(url_safe(f"/{last_page.get('label')}")) if badge.visible else None)
        fab.on('click', lambda: handle_path_change(warehouse=False))
        fab.bind_visibility_from(app.storage.user, 'Total', backward=lambda v: v > 0)
        fab.on('mouseenter', lambda: label.set_visibility(True), throttle=0.2)
        fab.on('mouseleave', lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot('label'):
            with ui.row():
                icon = ui.icon(last_page.get('icon'))
                label = ui.label(last_page.get('label')).classes('text-secondary text-base')
                label.set_visibility(False)
            badge = ui.badge('0', color='primary', text_color='secondary').props(
                "rounded floating").classes('text-bold')
            badge.bind_text_from(app.storage.user, 'Total')
            badge.bind_visibility_from(app.storage.user, 'Total', backward=lambda v: v > 0)


def tabs():
    return ui.tabs().classes('bg-secondary h-[56px] w-full scroll font-bold subpixel-antialiased tracking-widest m-0 p-0').props(
        'height=56px active-bg-color=accent inline-label mobile-arrows stretch')


def tab_panels(tabs:Tabs):
    return ui.tab_panels(tabs).classes('w-full h-dvh')
