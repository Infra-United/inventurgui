from nicegui import ui, app
from nicegui.elements.button import Button
from nicegui.elements.drawer import LeftDrawer
from nicegui.elements.tabs import Tabs

from inventurgui.helper.config import config, get_path, load_config
from inventurgui.helper.safe_url import url_safe, reverse_url
from inventurgui.helper.storage import Storage
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.auth import authenticate_user


def header(ld: LeftDrawer|None = None):
    """
	Creates the header bar on top of the screen using the logo, the title and the main menu. NOTE: Only used on Screens wider than 640px.
    :param ld:  The left drawer that holds the warehouse menu.
    """
    with ui.header().classes("fixed max-sm:hidden h-[56px] bg-primary flex-nowrap m-0 pr-3 p-0 items-center"):
        img = ui.image(source=get_path(config.get("favicon"))).classes("h-full m-0 p-0 w-[56px]").on('click', lambda: ui.navigate.to("/"))
        img.force_reload()
        ui.label(str(config.get("title")).upper()).classes("text-secondary w-[161px] max-lg:hidden text-bold text-xl")
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


def checkout_fab(next_page: dict[str, str]):
    props: str = "text-color=secondary"
    with ui.page_sticky(position="bottom-right", x_offset=18, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="navigate_next", direction="up").props(f"{props} active-icon='hourglass_top'")
        fab.on("click", lambda: ui.navigate.to(url_safe(f"/{next_page.get('label')}?id={app.storage.browser['id']}")))
        fab.on("mouseenter", lambda: label.set_visibility(True), throttle=0.2)
        fab.on("mouseleave", lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot("label"):
            with ui.row():
                ui.icon(next_page.get("icon"))
                label = ui.label(next_page.get("label")).classes("text-secondary text-base")
                label.set_visibility(False)
            badge = (
                ui.badge("0", color="primary", text_color="secondary").props("rounded floating").classes("text-bold")
            )
            badge.bind_text_from(app.storage.user, "Total")
            badge.bind_visibility_from(app.storage.user, "Total", backward=lambda v: v > 0)

@ui.refreshable
def main_menu(
    ld: LeftDrawer, classes: str = "stretch", props: str = "unelevated no-wrap text-color=secondary square"
) -> None:
    start: dict[str, str | dict[str, str]] = load_config()["start"]
    btn = ui.button(config['warehouse'].get('label'), icon="menu", on_click=lambda: ld.show())
    btn.classes(classes).props(f'{props} :visible=Quasar.Screen.lt.md')
    #ui.on('resize', lambda: btn.set_visibility(640 >= app.storage.user['screen'].get('width') >= 1024))
    start_btn: Button = ui.button(start.get("label"), icon=start.get("icon")).classes(classes).props(props)
    start_btn.on_click(lambda: ui.navigate.to("/"))
    if authenticate_user():
        requests: dict[str, str | dict[str, str]] = load_config()["requests"]
        requests_btn: Button = ui.button(requests.get('label'), icon=requests.get('icon')).classes(classes).props(props)
        requests_btn.on_click(lambda: ui.navigate.to(f"/{requests.get('label')}"))
    ui.space().classes("max-sm:hidden")
    if authenticate_user():
        for label in ["settings", "logout"]:
            btn: Button = ui.button(icon=label).classes(classes).props(props)
            btn.on_click(lambda l=label: ui.navigate.to(f"/{l}"))
            btn.on('mouseenter', lambda l=label, b=btn: b.set_text(f"{l}"))
            btn.on('mouseleave', lambda b=btn: b.set_text(""))

def tabs():
    return (
        ui.tabs()
        .classes("bg-secondary h-[56px] w-full scroll font-bold subpixel-antialiased tracking-widest m-0 p-0")
        .props("height=56px active-bg-color=accent inline-label mobile-arrows stretch")
    )


def tab_panels(tabs: Tabs):
    return ui.tab_panels(tabs).classes("w-full h-dvh")

@ui.refreshable
def warehouse_menu(warehouses: list[Warehouse], ld: LeftDrawer, classes: str, props: str):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    warehouse_conf: dict = load_config()["warehouse"]
    path_category = reverse_url(ui.context.client.sub_pages_router.current_path.split("/")[-1])
    path_warehouse = reverse_url(ui.context.client.sub_pages_router.current_path.split("/")[-2])

    #t = ui.tree([{'id': w.name, 'label': w.name.upper(), 'children': [{'id': c, 'label': c.upper()} for c in w.categories]} for w in warehouses])
    #t.props(f'{props} accordion no-connectors "selected-color=accent"').classes(classes)
    with ui.row().classes("flex bg-primary row w-full px-20 py-3 mb-1"):
        ui.icon(warehouse_conf.get("icon"), size="20px", color="secondary").classes(classes)
        ui.label(warehouse_conf.get("label").upper()).classes(classes).classes("text-secondary")

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
                    badge = (
                        ui.badge("0", color="primary", text_color="secondary").props().classes("text-bold ml-2")
                    )
                    badge.bind_text_from(app.storage.user, warehouse.name, backward=lambda v: str(len(v)), strict=False)
            if len(warehouse.categories) == 2:
                expansion.on("click", lambda: (ld.hide()) if Storage.width() < 1024 else None)
                continue
            categories = warehouse.categories
            categories[0] = config['admin']['edits'] if authenticate_user() else categories[0]
            toggle = ui.toggle(categories)
            toggle.set_value(path_category)
            expansion.on("click", lambda t=toggle: t.set_value(path_category))
            expansion.on(
                "click", lambda l=url_safe(name): ui.navigate.to(f"/{l}/{url_safe(warehouse_conf['everything'])}")
            )
            expansion.on("click", lambda e=expansion: e.open())
            toggle.classes(f"{classes} column").props("square unelevated stretch toggle-color=accent")
            toggle.on_value_change(lambda v, w=warehouse: ui.navigate.to(f"/{url_safe(w.name)}/{url_safe(v.value)}"))
            toggle.on_value_change(lambda: ld.hide() if Storage.width() < 1024 else None)


def back_fab(
    last_page: dict[str, str],
):
    props: str = "text-color=primary"
    with ui.page_sticky(position="bottom-left", x_offset=30, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="navigate_before", direction="up", color="secondary").props(f"{props}")
        fab.on("click", lambda: ui.navigate.to(url_safe(f"/{last_page.get('label')}?id={app.storage.browser['id']}")))
        fab.bind_visibility_from(app.storage.user, "Total", backward=lambda v: v > 0)
        fab.on("mouseenter", lambda: label.set_visibility(True), throttle=0.2)
        fab.on("mouseleave", lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot("label"):
            with ui.row():
                ui.icon(last_page.get("icon"))
                label = ui.label(last_page.get("label")).classes("text-base")
                label.set_visibility(False)
            badge = (
                ui.badge("0", color="secondary", text_color="primary").props("rounded floating").classes("text-bold")
            )
            badge.bind_text_from(app.storage.user, "Total")
            badge.bind_visibility_from(app.storage.user, "Total", backward=lambda v: v > 0)