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


def header(ld: LeftDrawer|None = None):
    """
	Creates the header bar on top of the screen using the logo, the title and the main menu. NOTE: Only used on Screens wider than 640px.
    :param ld:  The left drawer that holds the warehouse menu.
    """
    with (ui.header().classes("fixed max-sm:hidden h-[56px] bg-primary flex-nowrap m-0 pr-3 p-0 items-center")):
        img = ui.image(source=get_path(settings.favicon)).classes("h-full m-0 p-0 w-[56px]")
        img.on('click', lambda: ui.navigate.to("/"))
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
    with ui.left_drawer(bordered=True).classes("gap-y-2 p-0 items-stretch").props("width=250") as ld:
        ui.space().classes("sm:hidden")
        drawer_menu(warehouses, settings.warehouse, ld)
    return ld

def right_drawer(wiki_menu: list[WikiChapter]) -> RightDrawer:
    with ui.right_drawer(bordered=True).classes("gap-y-2 p-0 items-stretch").props("width=250") as rd:
        ui.space().classes("sm:hidden")
        drawer_menu([c for c in wiki_menu], settings.help, rd)
    return rd

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
        requests_btn.on_click(lambda: ui.navigate.to(f"/{slugify(settings.requests["label"])}"))
    ui.space().classes("max-sm:hidden")
    if authenticate_user():
        for label in ["settings", "logout"]:
            btn: Button = ui.button(icon=label).classes(classes).props(props)
            btn.on_click(lambda l=label: ui.navigate.to(f"/{slugify(l)}"))
    elif settings.help.get("display"):
        help_btn: Button = ui.button(settings.help["label"], icon=settings.help["icon"]).classes(classes).props(
            props)
        help_btn.on_click(lambda: ui.navigate.to(f"/{slugify(settings.help["label"])}"))


@ui.refreshable
def drawer_menu(menu_items: list[MenuItem], config:dict[str, str], ld: LeftDrawer | RightDrawer):
    """
    See https://github.com/zauberzeug/nicegui/discussions/5566 for some documentation.
    """
    classes: str = "text-center text-gray-200 m-0 p-0 subpixel-antialiased tracking-widest"
    def parse_uri(e: Expansion, t:Toggle):
        path_1 =  ui.context.client.sub_pages_router.current_path.split("/")[-1]
        path_2 =  ui.context.client.sub_pages_router.current_path.split("/")[-2]
        if path_2.upper() == e.text:
            e.open()
            t.set_value(path_1)
        else:
            e.open() if e.text == menu_items[0].name.upper() else e.close()


    #t = ui.tree([{'id': w.name, 'label': w.name.upper(), 'children': [{'id': c, 'label': c.upper()} for c in w.categories]} for w in warehouses])
    #t.props(f'{props} accordion no-connectors no-selection-unset selected-color=accent').classes(classes)
    #t.on_select(lambda e: (ui.notify(e.value), t.expand(e.value)))
    with ui.row().classes("flex bg-primary row  w-full px-20 py-3 mb-1"):
        ui.icon(config["icon"], size="20px", color="secondary").classes(classes)
        ui.label(config["label"].upper()).classes(classes).classes("text-secondary")

    for item in menu_items:
        children = [slugify(i) for i in item.children]
        with ui.expansion(text=item.name.upper(), group=config['label']).classes(classes) as exp:
            if isinstance(item, Warehouse):
                with exp.add_slot("header"):
                    with ui.label(item.name.upper()).classes("py-3 w-full"):
                        badge("0").bind_text_from(app.storage.user["selected"], item.name, backward=lambda v: len(v))

            exp.props(f"header-class='bg-secondary' popup hide-expand-icon")
            exp.on_value_change(
                lambda v, e=exp: e.props.update(
                    {"header-class": "bg-accent"} if v.value else {"header-class": "bg-secondary"}
                )
            )
            toggle = ui.toggle(children)
            parse_uri(exp, toggle)
            exp.on("click", lambda i=item: ui.navigate.to(f"/{slugify(i.name)}/{slugify(settings.warehouse['everything'])}"))
            exp.on("click", lambda t=toggle: t.set_value(slugify(settings.warehouse['everything'])))
            exp.on("click", lambda e=exp: e.open())
            toggle.classes(f"{classes} column").props("square unelevated stretch toggle-color=accent")
            toggle.on_value_change(lambda v, w=item: ui.navigate.to(f"/{slugify(w.name)}/{v.value}"))
            ui.on('resize', lambda e, t=toggle: t.on_value_change(lambda r=e: ld.hide() if r.args['width'] < 1024 else None), trailing_events=True)



