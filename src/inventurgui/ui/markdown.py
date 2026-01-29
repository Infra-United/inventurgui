import httpx
from nicegui import ui, run
from nicegui.elements.markdown import Markdown

from inventurgui.helper.config import get_path
from inventurgui.helper.logger import LOGGER


async def render_markdown(values: dict[str, str]) -> Markdown:
    label = values.get("label")
    path = get_path(values.get("path"))
    try:
        with open(path, "r") as f:  # open file
            LOGGER.debug(f"Creating {label} with the content of {path}...")
            text = f.read()
    except FileNotFoundError:
        text = (
            f"<br>path:{path.name}<br> in config for page **{label}** does not exist."
            f"<br>Please review your config, read the logs and check /files."
            f"<br>If you started the program for the first time i may have fetched the page by now."
            f"<br>In that case a page reload might also fix the problem."
        )
    return ui.markdown(text).classes(
        "p-10 pt-5 mx-auto text-justify hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180"
    )
