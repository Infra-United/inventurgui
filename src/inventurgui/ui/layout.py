from nicegui import ui
from nicegui.elements.button import Button
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.paths import get_path
from inventurgui.ui.helper.safe_url import url_safe, reverse_url
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.reusable_elements import selected_count_badge


def header(ld: LeftDrawer|None = None):
    """
	Creates the header bar on top of the screen using the logo, the title and the main menu. NOTE: Only used on Screens wider than 640px.
    :param ld:  The left drawer that holds the warehouse menu.
    """
    with (ui.header().classes("fixed max-sm:hidden h-[56px] bg-primary flex-nowrap m-0 pr-3 p-0 items-center")):
        img = ui.image(source=get_path(settings.favicon)).classes("h-full m-0 p-0 w-[56px]")
        img.on('click', lambda: ui.navigate.to("/"))
        img.force_reload()
        ui.label(str(settings.title).upper()).classes("text-secondary w-[161px] max-lg:hidden text-bold text-xl")
        main_menu(ld, classes="stretch h-full")


def footer(ld: LeftDrawer):
    """
	Creates the footer bar on bottoms of the screen using the main menu. NOTE: Only used on Screens smaller than 640px.
	:param ld: The left drawer that holds the warehouse menu.
    """
    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden p-0 gap-0 h-[56px]"):
        main_menu(
            ld,
            props='label="" unelevated no-wrap text-color=dark square',
            classes="flex-auto stretch h-full",
        )


def left_drawer(warehouses: list[Warehouse]) -> LeftDrawer:
    with ui.left_drawer(bordered=True).classes("gap-0 p-0 items-stretch").props("width=250") as ld:
        classes: str = "text-center text-gray-200 py-1 m-0 font-bold subpixel-antialiased tracking-widest"
        props: str = "unelevated square"
        ui.space().classes("sm:hidden")
        warehouse_menu(warehouses, ld, classes, props)
    return ld


@ui.refreshable
def main_menu(
    ld: LeftDrawer, classes: str = "stretch", props: str = "unelevated no-wrap text-color=secondary square"
) -> None:
    btn = ui.button(settings.warehouse['label'], icon="menu", on_click=lambda: ld.show())
    btn.classes(classes).props(f'{props} :visible=Quasar.Screen.lt.md')
    start_btn: Button = ui.button(settings.start["label"], icon=settings.start["icon"]).classes(classes).props(props)
    start_btn.on_click(lambda: ui.navigate.to("/"))
    if authenticate_user():
        requests_btn: Button = ui.button(settings.requests["label"], icon=settings.requests["icon"])
        requests_btn.classes(classes).props(props)
        requests_btn.on_click(lambda: ui.navigate.to(f"/{settings.requests["label"]}"))
    ui.space().classes("max-sm:hidden")
    if authenticate_user():
        for label in ["settings", "logout"]:
            btn: Button = ui.button(icon=label).classes(classes).props(props)
            btn.on_click(lambda l=label: ui.navigate.to(f"/{l}"))


@ui.refreshable
def warehouse_menu(warehouses: list[Warehouse], ld: LeftDrawer, classes: str, props: str):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    path_category = reverse_url(ui.context.client.sub_pages_router.current_path.split("/")[-1])
    path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split("/")[-2])
    #t = ui.tree([{'id': w.name, 'label': w.name.upper(), 'children': [{'id': c, 'label': c.upper()} for c in w.categories]} for w in warehouses])
    #t.props(f'{props} accordion no-connectors no-selection-unset selected-color=accent').classes(classes)
    #t.on_select(lambda e: (ui.notify(e.value), t.expand(e.value)))
    with ui.row().classes("flex bg-primary row w-full px-20 py-3 mb-1"):
        ui.icon(settings.warehouse["icon"], size="20px", color="secondary").classes(classes)
        ui.label(settings.warehouse["label"].upper()).classes(classes).classes("text-secondary")

    for warehouse in warehouses:
        name = warehouse.name
        with ui.expansion(group="menu").classes(classes) as expansion:
            expansion.props(f"{props} header-class='bg-secondary' hide-expand-icon")
            expansion.on_value_change(
                lambda v, e=expansion: e.props.update(
                    {"header-class": "bg-accent"} if v.value else {"header-class": "bg-secondary"}
                )
            )
            expansion.set_value(True if name == path_warehouse else True if name == warehouses[0].name else False)
            with expansion.add_slot("header"):
                with ui.label(name.upper()).classes("py-3 w-full"):
                    selected_count_badge(warehouse.name)
            if len(warehouse.categories) == 2:
                ui.on('resize',
                      lambda e, x=expansion: x.on('click', lambda r=e: ld.hide() if r.args['width'] < 1024 else None))
                continue
            categories = warehouse.categories
            categories[0] = i18n.get('admin.edits') if authenticate_user() else categories[0]
            toggle = ui.toggle(categories)
            toggle.set_value(path_category)
            expansion.on("click", lambda t=toggle: t.set_value(path_category))
            expansion.on(
                "click", lambda l=url_safe(name): ui.navigate.to(f"/{l}/{url_safe(settings.warehouse['everything'])}")
            )
            expansion.on("click", lambda e=expansion: e.open())
            toggle.classes(f"{classes} column").props("square unelevated stretch toggle-color=accent")
            toggle.on_value_change(lambda v, w=warehouse: ui.navigate.to(f"/{url_safe(w.name)}/{url_safe(v.value)}"))
            ui.on('resize', lambda e, t=toggle: t.on_value_change(lambda r=e: ld.hide() if r.args['width'] < 1024 else None), trailing_events=True)



