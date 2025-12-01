from contextlib import contextmanager

from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import config
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.nextcloud import Warehouse


def main_menu(warehouses:list[Warehouse], classes:str="stretch", props:str="flat square"):
    (ui.button(icon='help_outline', on_click=lambda l=config['help']['label']: ui.navigate.to(f"/"))
     .classes(classes).props(props))
    for warehouse in warehouses:
        (ui.button(warehouse['name'], on_click=lambda l=url_safe(warehouse['name']): ui.navigate.to(f"/{l}"))
        .classes(classes).props(props))


def secondary_menu(warehouse:Warehouse,
              classes:str="w-full text-secondary py-2 font-normal subpixel-antialiased tracking-widest border-black",
              props:str="flat square"):
    categories = sorted(warehouse.inventory[config['data']['category']].unique())
    if len(warehouse.categories) > 1:
        for category in warehouse.categories:
            ui.button(category, on_click=lambda c=url_safe(category): ui.navigate.to(f"/{warehouse.name}/{c}")).classes(classes).props(props)

@contextmanager
def header(warehouses:list[Warehouse]):
    with ui.header().classes("fixed max-sm:hidden flex-nowrap bg-secondary m-0 px-3 py-2 border-none items-center"):
        main_menu(warehouses)
        ui.space().classes()
        """
        ui.space().classes("max-lg:hidden")
        with ui.row().classes("lg:hidden"):
            with ui.dropdown_button('Kategorien', auto_close=True).props("flat square"):
                secondary_menu(pages)"""

def left_drawer(warehouse:Warehouse) -> LeftDrawer:
    with ui.left_drawer(value=True, fixed=True).classes("flex-nowrap py-3 px-0 gap-0 items-stretch bg-dark").props('width=250') as ld:
        ui.space().classes("sm:hidden")
        secondary_menu(warehouse)
        ui.button(icon="close", on_click=lambda: ld.hide()).props("flat color=contrast align=center").classes("lg:hidden h-24px")
    return ld

