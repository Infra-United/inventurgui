from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.drawer import LeftDrawer, RightDrawer
from nicegui.elements.fab import FabAction

from inventurgui.helper.config import config
from inventurgui.helper.safe_url import url_safe, reverse_url
from inventurgui.io.warehouse import Warehouse


def main_menu(rd:RightDrawer, classes:str="stretch", props:str="unelevated no-wrap text-color=secondary square"):
    help_button = ui.button(config['help']['label'], icon=config['help']['icon']).classes(classes).props(props)
    help_button.on_click(lambda l=url_safe(config['help']['label']): ui.navigate.to(f"/"))
    help_button.on_click(lambda: rd.hide())
    with ui.button(config['truck']['label'], icon=config['truck']['icon']).classes(classes).props(props) as truck_button:
        truck_button.on_click(lambda l=url_safe(config['truck']['label']): ui.navigate.to(f"/{l}"))
        truck_button.on_click(lambda: rd.hide())
        badge = ui.badge('0', color='white', text_color='dark').props(
            "rounded floating")
        badge.bind_text_from(app.storage.user, 'Total')
    form_button = ui.button(config['form']['label'],icon=config['form']['icon']).classes(classes).props(props)
    form_button.on_click(lambda l=url_safe(config['form']['label']): ui.navigate.to(f"/{url_safe(config['form']['label'])}"))
    form_button.on_click(lambda: rd.hide())
    #form_button.on_click(lambda: form_button.classes(add=''))
    ui.space().classes('max-sm:hidden')
    ui.button(config['warehouse']['label'], on_click=lambda: rd.show(), icon=config['warehouse']['icon']).classes(classes).props(props)

def warehouse_menu(warehouses:list[Warehouse], rd:RightDrawer,
                   classes:str="w-full text-center text-primary py-2 font-bold subpixel-antialiased tracking-widest",
                   props:str="unelevated square hide-expand-icon popup"):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    path_category = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-1])
    path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-2])
    for warehouse in warehouses:
        name = warehouse.name
        with ui.expansion(group='menu').classes(classes) as expansion:
            expansion.props(f"{props} header-class='bg-dark'")
            expansion.on_value_change(lambda v, e=expansion: e.props.update(
                {"header-class": 'bg-primary text-dark'} if v.value else {
                    "header-class": 'bg-dark'}))
            expansion.set_value(True if name == path_warehouse else False)
            expansion.on('click', lambda l=url_safe(name): ui.navigate.to(f"/{l}/{url_safe(config['everything'])}"))
            expansion.on('click', lambda e=expansion: e.open())
            with expansion.add_slot('header'):
                with ui.label(name.upper()).classes('w-full'):
                    badge = ui.badge('0', color='white', text_color='dark').props("rounded floating")
                    badge.bind_text_from(app.storage.user, warehouse.name, backward=lambda v:str(len(v)), strict=False)
            toggle = ui.toggle(warehouse.categories)
            toggle.set_value(path_category)
            toggle.classes(f"{classes} column").props('square unelevated toggle-text-color=dark')
            toggle.on_value_change(lambda v, w=warehouse: ui.navigate.to(f"/{url_safe(w.name)}/{url_safe(v.value)}"))
            expansion.on('click', lambda t=toggle: t.set_value(config['everything']))
            toggle.on_value_change(lambda: rd.hide() if app.storage.user.get('screen')['width'] < 1024 else None)


def header(rd:RightDrawer):
    with ui.header().classes("fixed max-sm:hidden h-[56px] flex-nowrap m-0 px-3 border-none items-center"):
        main_menu(rd)

def footer(rd:RightDrawer):
    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden p-2"):
        main_menu(rd,
            props='label="" unelevated no-wrap text-color=secondary square',
            classes="flex-auto m-0 p-0",
        )

def right_drawer(warehouses:list[Warehouse]) -> RightDrawer:
    with ui.right_drawer().classes("py-3 px-0 items-stretch bg-dark").props('width=250') as rd:
        ui.space().classes("sm:hidden")
        path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-2])
        [rd.set_value(True if w.name == path_warehouse else False) for w in warehouses]
        warehouse_menu(warehouses, rd)
    return rd


def tool_buttons(grid:AgGrid, classes:str="stretch", props:str=""):
    with ui.page_sticky(x_offset=18, y_offset=18).classes('z-999'):
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

