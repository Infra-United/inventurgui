from contextlib import contextmanager

from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import config
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.nextcloud import Warehouse


def main_menu(warehouses:list[Warehouse], ld:LeftDrawer, classes:str="stretch", props:str="flat square"):
    ui.button(on_click=lambda: ld.toggle(), icon="menu").classes(classes).props(props)
    (ui.button(icon='help_outline', on_click=lambda l=config['help']['label']: ui.navigate.to(f"/"))
     .classes(classes).props(props))
    for warehouse in warehouses:
        (ui.button(warehouse['name'], on_click=lambda l=url_safe(warehouse['name']): ui.navigate.to(f"/{l}"))
        .classes(classes).props(props))

@ui.refreshable
def secondary_menu(warehouse:Warehouse, ld:LeftDrawer,
              classes:str="w-full text-secondary py-2 font-normal subpixel-antialiased tracking-widest border-black",
              props:str="square toggle-color=secondary"):
    inventory = warehouse["inventory"]
    categories = sorted(inventory[config['data']['category']].unique())
    everything = url_safe(config['everything']['label'])
    if len(categories) > 1:
        categories.insert(0, everything)
        ld.clear()
        with ld:
            ui.toggle(categories, value=everything, on_change=lambda v:ui.navigate.to(f"/{url_safe(warehouse['name'])}/{url_safe(v.value)}")).classes(classes).props(props).classes('wrap column')
    else:
        ld.clear()
        with ld:
            ui.toggle([everything], value=everything).classes(classes).props(props).classes('wrap column')
@contextmanager
def header(warehouses:list[Warehouse], ld:LeftDrawer):
    with ui.header().classes("fixed max-sm:hidden flex-nowrap bg-secondary m-0 px-3 py-2 border-none items-center"):
        main_menu(warehouses, ld)
        ui.space().classes()
        """
        ui.space().classes("max-lg:hidden")
        with ui.row().classes("lg:hidden"):
            with ui.dropdown_button('Kategorien', auto_close=True).props("flat square"):
                secondary_menu(pages)"""

@contextmanager
def footer(warehouses:list[Warehouse], ld:LeftDrawer):
    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden bg-secondary p-2"):
        main_menu(warehouses, ld,
            props='label="" flat',
            classes="flex-auto bg-secondary m-0 p-0",
        )

def left_drawer() -> LeftDrawer:
    with ui.left_drawer(value=True, fixed=True).classes("flex-nowrap py-3 px-0 gap-0 items-stretch bg-dark").props('width=250') as ld:
        ui.space().classes("sm:hidden")
        ui.button(icon="close", on_click=lambda: ld.hide()).props("flat color=contrast align=center").classes("lg:hidden h-24px")
    return ld

