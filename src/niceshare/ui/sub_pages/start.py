from nicegui import ui

from niceshare.io.selection import SELECTION_ROOT


def start_page(md: dict[str, str]) -> None:
    ui.navigate.to(f"/{SELECTION_ROOT}")
    """LOGGER.debug("Creating start page...")
    ui.page_title(settings.title)
    with ui.tab_panel(settings.start["label"]).classes("m-0 p-0 max-sm:pb-20 w-full scroll h-dvh"):
        render_markdown(md.get(settings.start["label"]))
    """