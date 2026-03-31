from typing import Tuple

from nicegui import ui, app
from nicegui.elements.button import Button
from nicegui.elements.drawer import LeftDrawer, RightDrawer
from nicegui.elements.expansion import Expansion
from nicegui.elements.toggle import Toggle
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.io.warehouse import Warehouse
from inventurgui.io.wiki import WikiChapter, MenuItem
from inventurgui.ui.auth import authenticate_user
from inventurgui.ui.helper.reusable_elements import badge


def create_layout(
    warehouses: list[Warehouse], wiki_menu: list[WikiChapter] | None
) -> Tuple[LeftDrawer, RightDrawer | None]:
    # Drawers
    with ui.left_drawer(bordered=True).classes("gap-y-2 p-0 items-stretch").props("width=250") as ld:
        ui.space().classes("sm:hidden")
    if wiki_menu:
        with ui.right_drawer(bordered=True).classes("gap-y-2 p-0 items-stretch").props("width=250") as rd:
            ui.space().classes("sm:hidden")
            drawer_menu([c for c in wiki_menu], settings.help)
    with ld:
        drawer_menu(warehouses, settings.warehouse)

    # Header
    with ui.header().classes("fixed max-sm:hidden h-[56px] bg-primary flex-nowrap m-0 pr-3 p-0 items-center"):
        img = ui.image(source=get_path(settings.logo)).classes("h-full m-0 p-0 w-[56px]")
        img.on("click", lambda: ui.navigate.to("/"))
        ui.label(str(settings.title).upper()).classes("text-secondary w-[161px] max-lg:hidden text-bold text-xl")
        main_menu(ld, rd if wiki_menu else None, classes="stretch h-full")

    # Footer is only shown on small screens
    with ui.footer(fixed=True).classes("sm:hidden p-0 gap-0 h-[56px]"):
        main_menu(
            ld,
            rd if wiki_menu else None,
            props='label="" unelevated no-wrap text-color=dark square',
            classes="flex-auto stretch h-full",
        )
    return ld, rd if wiki_menu else None


@ui.refreshable
def main_menu(
    ld: LeftDrawer,
    rd: None | RightDrawer,
    classes: str = "stretch",
    props: str = "unelevated push no-wrap text-color=secondary square",
) -> None:
    warehouse_btn = ui.button(settings.warehouse["label"], icon=settings.warehouse["icon"], on_click=lambda: ld.show())
    warehouse_btn.on_click(lambda: (ui.navigate.to(f"/{slugify(settings.warehouse['label'])}"), drawer_menu.refresh()))
    warehouse_btn.classes(classes).props(props)
    start_btn: Button = ui.button(settings.start["label"], icon=settings.start["icon"]).classes(classes).props(props)
    start_btn.on_click(lambda: ui.navigate.to("/"))
    if authenticate_user():
        requests_btn: Button = ui.button(settings.requests["label"], icon=settings.requests["icon"])
        requests_btn.classes(classes).props(props)
        requests_btn.on_click(lambda: ui.navigate.to(f"/{slugify(settings.requests['label'])}"))
    ui.space().classes("max-sm:hidden")
    if authenticate_user():
        for label in ["settings", "logout"]:
            btn: Button = ui.button(icon=label).classes(classes).props(props)
            btn.on_click(lambda l=label: ui.navigate.to(f"/{slugify(l)}"))
    elif settings.help.get("display"):
        help_btn: Button = ui.button(
            settings.help["label"], icon=settings.help["icon"], on_click=lambda: rd.show() if rd else None
        )
        help_btn.classes(classes).props(props)
        help_btn.on_click(lambda: (ui.navigate.to(f"/{slugify(settings.help['label'])}"), drawer_menu.refresh()))


@ui.refreshable
def drawer_menu(
    menu_items: list[MenuItem],
    config: dict[str, str],
):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    menu_root = slugify(config["label"])

    def parse_uri(e: Expansion, t: Toggle):
        path_1 = ui.context.client.sub_pages_router.current_path.split("/")[-1]
        path_2 = ui.context.client.sub_pages_router.current_path.split("/")[-2]
        if path_2 == e.text:
            e.open()
            t.set_value(path_1)
        else:
            if e.text == menu_items[0].name:
                e.open()
                t.set_value(menu_items[0].name)

    classes: str = "text-center text-gray-200 text-bold m-0 subpixel-antialiased tracking-widest"
    with ui.row().classes("flex bg-primary row w-full px-20 py-3 mb-1") as row:
        ui.icon(config["icon"], size="20px", color="secondary").classes(classes)
        ui.label(config["label"].upper()).classes(classes).classes("text-secondary text-bold")
        row.on("click", lambda: (ui.navigate.to(f"/{menu_root}"), drawer_menu.refresh()))

    for idx, item in enumerate(menu_items):
        with ui.expansion(text=item.name, group=config["label"]).classes(f"{classes} mx-2") as exp:
            with exp.add_slot("header"):
                with ui.label(item.name).classes("py-3 text-base/7 w-full"):
                    if isinstance(item, Warehouse):
                        badge("0").bind_text_from(app.storage.user["selected"], item.name, backward=lambda v: len(v))

            exp.props("header-class='border' dense hide-expand-icon")
            exp.on_value_change(
                lambda v, e=exp: e.props.update(
                    {"header-class": "bg-accent"} if v.value else {"header-class": "bg-dark border"}
                )
            )
            toggle = ui.toggle(item.children)
            parse_uri(exp, toggle)
            exp.on("click", lambda t=toggle, i=item: t.set_value(i.name if i.name in t.options else t.options[0]))
            exp.on("click", lambda e=exp: e.open())
            exp.on("click", lambda i=item, t=toggle: ui.navigate.to(i.routes.get(t.value)))
            toggle.classes(f"{classes} column").props('stretch ripple unelevated no-caps padding="4px 8px" toggle-color=accent')
            toggle.on_value_change(lambda v, i=item: ui.navigate.to(i.routes.get(v.value)))
