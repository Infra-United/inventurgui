from contextlib import suppress

from nicegui import ui, app
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import load_config, config
from inventurgui.helper.storage import Storage
from inventurgui.ui.layout import tabs, tab_panels
from inventurgui.ui.markdown import render_markdown


async def start_page(ld: LeftDrawer) -> None:
    start: dict[str, str | dict[str, str]] = load_config()["start"]
    main_tabs = tabs()
    main_panels = tab_panels(main_tabs)

    ui.page_title(f"{config['title']}")
    for key, values in start.items():
        if isinstance(values, str) or not values.get("display"):
            continue
        with main_tabs:
            label = values.get("label")
            ui.tab(label, icon=values.get("icon"))
        with main_panels:
            with ui.tab_panel(label).classes("m-0 p-0"):
                await render_markdown(values)
    main_panels.set_value([t.props.get("label") for t in main_tabs.descendants()][0])  # First tab is open by default
    with suppress(TypeError):
        ld.show() if Storage.width() >= 1024 else ld.hide()
