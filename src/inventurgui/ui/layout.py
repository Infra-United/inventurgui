import time

from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.drawer import LeftDrawer, RightDrawer
from nicegui.elements.fab import FabAction

from inventurgui.helper.config import config, menu, get_path
from inventurgui.helper.safe_url import url_safe, reverse_url
from inventurgui.io.warehouse import Warehouse


def main_menu(ld:LeftDrawer, classes:str="stretch", props:str="unelevated no-wrap text-color=secondary square"):
    for key, values in menu.items():
        btn = ui.button(values['label'], icon=values['icon']).classes(classes).props(props)
        if key == 'start':
            btn.on_click(lambda: ui.navigate.to(f"/"))
        elif key == 'warehouse':
            btn.classes(f"{classes} lg:hidden").on_click(lambda: ld.show())
        else:
            btn.on_click(lambda l=url_safe(values['label']): ui.navigate.to(f"/{l}"))
        if key == 'truck':
            with btn:
                badge = ui.badge('0', color='primary', text_color='secondary').props(
                    "rounded floating").classes('text-bold')
                badge.bind_text_from(app.storage.user, 'Total')
    #form_button.on_click(lambda: form_button.classes(add=''))

def warehouse_menu(warehouses:list[Warehouse], ld:LeftDrawer, classes:str, props:str):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    path_category = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-1])
    path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-2])
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
            toggle.on_value_change(lambda: (ld.hide()) if app.storage.user.get('screen')['width'] < 1024 else None)


def header(ld:LeftDrawer):
    with ui.header().classes("fixed max-sm:hidden h-[56px] bg-primary flex-nowrap m-0 pr-3 p-0 items-center"):
        ui.image(source=get_path(config.get('favicon'))).classes('h-full m-0 p-0 w-[56px]').on('click', lambda: ui.navigate.to("/"))
        ui.label(str(config.get('title')).upper()).classes('text-secondary max-lg:hidden text-bold text-xl').on('click', lambda: ui.navigate.to("/"))
        ui.space().classes('max-sm:hidden')
        main_menu(ld)

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
        with ui.row().classes('flex bg-primary row w-full px-20 py-3 mb-1'):
            ui.icon(config['menu']['warehouse']['icon'], size='20px', color='secondary').classes(classes)
            ui.label(config['menu']['warehouse']['label'].upper()).classes(classes).classes('text-secondary')
        warehouse_menu(warehouses, ld, classes, props)
    return ld


def tool_buttons(grid:AgGrid, classes:str="stretch", props:str="text-color=secondary"):
    with ui.page_sticky(x_offset=18, y_offset=18).classes('z-999'):
        #TODO Tooltip
        #ui.tooltip("Hier findest du ein paar Werkzeuge.").props('left')
        with ui.fab(icon='construction', direction='up').classes(classes).props(props):
            ui.fab_action(icon='zoom_out', on_click=lambda e: handle_theme_change(e.sender ,grid)).classes(classes).props(props)
            ui.fab_action(icon='select_all', on_click=lambda: grid.run_grid_method('selectAll')).classes(classes).props(props)
            ui.fab_action(icon='deselect', on_click=lambda: grid.run_grid_method('deselectAll')).classes(classes).props(props)

def handle_theme_change(e:FabAction, grid:AgGrid):
    current_theme = app.storage.user['grid_theme'] if app.storage.user.get('grid_theme') else 'alpine'
    match current_theme:
        case 'alpine':
            app.storage.user['grid_theme'] = 'balham'
            e.set_icon('zoom_in')
        case 'balham':
            app.storage.user['grid_theme'] = 'alpine'
            e.set_icon('zoom_out')
    e.bind_icon_to(grid, 'theme', forward=lambda i: 'balham' if i == 'zoom_in' else 'alpine')
    for row in app.storage.user[grid.props['options']['headerName']]:
        grid.run_row_method(row, 'setSelected', True)

