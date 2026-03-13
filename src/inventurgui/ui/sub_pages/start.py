from contextlib import suppress

from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.ui.helper.reusable_elements import tabs, tab_panels
from inventurgui.ui.helper.markdown import render_markdown


def start_page(ld: LeftDrawer, md: dict[str,str]) -> None:
    main_tabs = tabs()
    main_panels = tab_panels(main_tabs)
    LOGGER.debug("Creating start page...")
    ui.page_title(settings.title)
    for key, values in settings.start.items():
        if isinstance(values, str) or not values.get("display"):
            continue
        with main_tabs:
            label = values.get("label")
            ui.tab(label, icon=values.get("icon"))
        with main_panels:
            with ui.tab_panel(label).classes("m-0 p-0"):
                pass
                render_markdown(md.get(label))
    main_panels.set_value([t.props.get("label") for t in main_tabs.descendants()][0])  # First tab is open by default
    with suppress(TypeError):
        ui.on('resize', lambda e: ld.show() if e.args['width'] >= 1024 else ld.hide(), trailing_events=True)
