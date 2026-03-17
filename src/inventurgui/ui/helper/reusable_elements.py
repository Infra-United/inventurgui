from nicegui import ui, app
from nicegui.elements.tabs import Tabs
from slugify import slugify

from inventurgui.helper.i18n import i18n
from inventurgui.ui.auth import authenticate_user


def badge(text:str):
    return ui.badge(text, color="primary", text_color="secondary").props().classes("text-bold ml-2 py-1")

def tabs():
    return (
        ui.tabs()
        .classes("bg-secondary text-gray-200 h-[56px] w-full scroll font-bold subpixel-antialiased tracking-widest m-0 p-0")
        .props("height=56px active-bg-color=accent inline-label mobile-arrows stretch")
    )

def tab_panels(_tabs: Tabs):
    return ui.tab_panels(_tabs).classes("w-full h-dvh")

def next_fab(next_page: dict[str, str]):
    props: str = "text-color=secondary"
    if admin := authenticate_user():
        next_page = {'icon': 'save', 'label': (i18n.get('admin.save'))}
    with ui.page_sticky(position="bottom-right", x_offset=18, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="navigate_next", direction="up").props(f"{props} active-icon='hourglass_top'")
        if admin:
            fab.on('click', lambda: ui.notify('saving...')) # TODO handle save
        else:
            fab.on("click", lambda: ui.navigate.to(f"/{slugify(next_page.get('label'))}?id={app.storage.browser['id']}"))
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


def back_fab(last_page: dict[str, str]):
    props: str = "text-color=primary"
    with ui.page_sticky(position="bottom-left", x_offset=30, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="navigate_before", direction="up", color="secondary").props(f"{props}")
        fab.on("click", lambda: ui.navigate.to(f"/{slugify(last_page.get('label'))}?id={app.storage.browser['id']}"))
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


