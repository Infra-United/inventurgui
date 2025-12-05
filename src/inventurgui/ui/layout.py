from contextlib import contextmanager

from nicegui import ui, app
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import config
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.warehouse import Warehouse


def main_menu(ld:LeftDrawer, classes:str="stretch", props:str="flat square"):
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


@contextmanager
def header(ld:LeftDrawer):
    with ui.header().classes("fixed max-sm:hidden flex-nowrap bg-secondary m-0 px-3 py-2 border-none items-center"):
        ui.button(on_click=lambda: ld.toggle(), icon="menu").classes("lg:hidden stretch").props('flat square')
        main_menu(ld)
        ui.space().classes()
        """
        ui.space().classes("max-lg:hidden")
        with ui.row().classes("lg:hidden"):
            with ui.dropdown_button('Kategorien', auto_close=True).props("flat square"):
                secondary_menu(pages)"""

@contextmanager
def footer(ld:LeftDrawer):
    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden bg-secondary p-2"):
        ui.button(on_click=lambda: ld.toggle(), icon="menu").classes("stretch").props('flat square')
        main_menu(ld,
            props='label="" flat',
            classes="flex-auto bg-secondary m-0 p-0",
        )

def left_drawer(warehouses:list[Warehouse]) -> LeftDrawer:
    with ui.left_drawer().classes("py-3 px-0 gap-0 items-stretch bg-dark").props('width=250') as ld:
        warehouse_menu(warehouses, ld)
    return ld

