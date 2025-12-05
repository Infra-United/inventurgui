from nicegui import ui, app
from nicegui.elements.aggrid import AgGrid
from nicegui.elements.drawer import LeftDrawer
from nicegui.elements.fab import FabAction

from inventurgui.helper.config import config
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.warehouse import Warehouse


def main_menu(ld:LeftDrawer, classes:str="stretch", props:str="flat square"):
    ui.button(on_click=lambda: ld.toggle(), icon="menu").classes(f"{classes} lg:hidden").props(props)
    (ui.button(icon='help_outline', on_click=lambda l=config['help']['label']: ui.navigate.to(f"/"))
     .classes(classes).props(props))

def warehouse_menu(warehouses:list[Warehouse], ld:LeftDrawer,
                   classes:str="w-full text-secondary text-center py-2 font-bold subpixel-antialiased tracking-widest",
                   props:str="flat square hide-expand-icon popup"):
    for warehouse in warehouses:
        name = warehouse.name
        with (ui.expansion(name.upper(),value=True if name == warehouses[0].name else False, group='menu').classes(classes).props(props)
            .on('click', lambda l=url_safe(name): ui.navigate.to(f"/{l}"))):
            category_menu(warehouse, ld)

def category_menu(warehouse:Warehouse, ld:LeftDrawer,
              classes:str="w-full h-full text-secondary font-normal subpixel-antialiased tracking-widest",
              props:str="square unelevated toggle-color=secondary"):
    ui.toggle(warehouse.categories, value=warehouse.categories[0],
              on_change=lambda v:ui.navigate.to(f"/{url_safe(warehouse.name)}/{url_safe(v.value)}")
              ).classes(classes).props(props).classes('column')

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
        warehouse_menu(warehouses, ld)
        ui.button(icon="close", on_click=lambda: ld.hide()).props("flat color=contrast align=center").classes("h-24px lg:hidden")
    return ld


def tool_buttons(grid:AgGrid, classes:str="stretch bg-secondary", props:str="push glosssy color=secondary"):
    with ui.page_sticky(x_offset=18, y_offset=18):
        with ui.fab(icon='construction', direction='up').classes(classes).props(props):
            ui.fab_action(icon='zoom_out', on_click=lambda e: handle_theme_change(e.sender ,grid)).classes(classes).props(props)
            ui.fab_action(icon='select_all', on_click=lambda: grid.run_grid_method('selectAll')).classes(classes).props(props)
            ui.fab_action(icon='deselect', on_click=lambda: grid.run_grid_method('deselectAll')).classes(classes).props(props)

def handle_theme_change(e:FabAction, grid:AgGrid):
    current_theme = app.storage.user.get('grid_theme')
    match current_theme:
        case 'alpine':
            app.storage.user['grid_theme'] = 'balham'
            e.set_icon('zoom_in')
        case 'balham':
            app.storage.user['grid_theme'] = 'alpine'
            e.set_icon('zoom_out')
    e.bind_icon_to(grid, 'theme', forward=lambda i: 'balham' if i == 'zoom_in' else 'alpine')

