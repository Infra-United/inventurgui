from contextlib import suppress

from nicegui import app, ui, PageArguments
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.helper.magic_links import load_data_from_magic_link
from inventurgui.ui.helper.markdown import render_markdown
from inventurgui.ui.helper.request_form import Form
from inventurgui.ui.helper.reusable_elements import back_fab, tabs, tab_panels


# TODO check why the formatting is incorrect with default_conf


async def form_page(ld: LeftDrawer, warehouses: list[Warehouse], md: dict[str, str], args: PageArguments) -> None:
    form: dict[str, str | dict[str, str]] = settings.form

    ui.page_title(f"{form['label']}")

    def set_panel(screen: dict[str, int]):
        if screen["width"] < 1280:
            with suppress(IndexError):
                # First tab is open by default
                form_panels.set_value([t.props.get("label") for t in form_tabs.descendants()][0])
        else:
            form_panels.set_value("default")

    current_id = app.storage.browser["id"]
    request_id = args.query_parameters.get("id")
    if current_id != request_id:
        load_data_from_magic_link(current_id, request_id)

    ld.hide()
    terms = form.get("terms")
    form_tabs = tabs()
    form_panels = tab_panels(form_tabs)
    back_fab(settings.cart)
    with form_tabs.classes("xl:hidden"):
        with form_tabs:
            ui.tab(form.get("tab_label"), icon=form.get("tab_icon")).classes("px-7").props("inline-label")
            if terms.get("display"):
                ui.tab(terms.get("label"), icon=terms.get("icon")).props("inline-label")
    with form_panels:
        with ui.tab_panel("default").classes("xl:w-350 mx-auto p-5"):
            with ui.grid(columns=2) as grid:
                Form().create(warehouses)
                if terms.get("display"):
                    render_markdown(md.get(form.get("terms").get("label")))
        with ui.tab_panel(form.get("tab_label")).classes("m-0"):
            Form().create(warehouses)
        if terms.get("display"):
            with ui.tab_panel(terms.get("label")).classes("m-0 p-0"):
                render_markdown(md.get(form.get("terms").get("label")))
    ui.on("resize", lambda e: set_panel(e.args), throttle=1, trailing_events=True)
