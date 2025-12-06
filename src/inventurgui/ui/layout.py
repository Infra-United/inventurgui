from nicegui import ui, app, PageArguments, context
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.drawer import LeftDrawer
from nicegui.elements.expansion import Expansion
from nicegui.elements.fab import FabAction

from inventurgui.helper.config import config
from inventurgui.helper.safe_url import url_safe, reverse_url
from inventurgui.io.warehouse import Warehouse


def main_menu(ld:LeftDrawer, classes:str="stretch", props:str="flat square"):
    ui.button(on_click=lambda: ld.toggle(), icon="menu").classes(f"{classes} lg:hidden").props(props)
    (ui.button(icon='help_outline', on_click=lambda l=config['help']['label']: ui.navigate.to(f"/"))
     .classes(classes).props(props))

def warehouse_menu(warehouses:list[Warehouse],
                   classes:str="w-full text-secondary text-center py-2 font-bold subpixel-antialiased tracking-widest",
                   props:str="flat square hide-expand-icon popup"):
    path_category = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-1])
    path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split('/')[-2])
    for warehouse in warehouses:
        name = warehouse.name
        with ui.expansion(group='menu').classes(classes).props(props) as expansion:
            expansion.set_value(True if name == path_warehouse else False)
            expansion.on('click', lambda l=url_safe(name): ui.navigate.to(f"/{l}/{url_safe(config['everything'])}"))
            expansion.on('click', lambda e=expansion: e.open())
            with expansion.add_slot('header'):
                with ui.label(name.upper()).classes('w-full'):
                    badge = ui.badge('0', color='secondary', outline=True).props("transparent floating")
                    badge.bind_text_from(app.storage.user, warehouse.name, backward=lambda v:str(len(v)), strict=False)
            toggle = ui.toggle(warehouse.categories)
            toggle.set_value(path_category)
            toggle.classes(f"{classes} column").props('square unelevated toggle-color=secondary')
            toggle.on_value_change(lambda v, w=warehouse: ui.navigate.to(f"/{url_safe(w.name)}/{url_safe(v.value)}"))
            expansion.on('click', lambda t=toggle: t.set_value(config['everything']))
            toggle.on_value_change(lambda v, t=toggle: ui.notify([v.value, t.value]))


def header(ld:LeftDrawer):
    with ui.header().classes("fixed max-sm:hidden flex-nowrap bg-secondary m-0 px-3 py-2 border-none items-center"):
        main_menu(ld)
        ui.space().classes()

def footer(ld:LeftDrawer):
    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden bg-secondary p-2"):
        main_menu(ld,
            props='label="" flat',
            classes="flex-auto bg-secondary m-0 p-0",
        )

def left_drawer(warehouses:list[Warehouse]) -> LeftDrawer:
    with ui.left_drawer().classes("py-3 px-0 items-stretch bg-dark").props('width=250') as ld:
        ui.space().classes("sm:hidden")
        warehouse_menu(warehouses)
        ui.button(icon="close", on_click=lambda: ld.hide()).props("flat color=contrast align=center").classes("h-24px lg:hidden")
    return ld


def tool_buttons(grid:AgGrid, classes:str="stretch bg-secondary", props:str="push glossy color=secondary"):
    with ui.page_sticky(x_offset=18, y_offset=18):
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

