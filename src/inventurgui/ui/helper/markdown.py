from typing import Generator

from nicegui import ui
from nicegui.elements.markdown import Markdown

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path


def render_markdown(text: str|None = "") -> Markdown:
    return ui.markdown(text).classes(
        "p-10 pt-5 mx-auto text-justify wrap-break-word hyphens-none lg:text-base/6 md:text-sm/5 sm:antialiasing text-gray-300 max-w-180"
    )


def read_page_files() -> Generator[tuple[str, str], None, None]:
    for idx, page_conf in enumerate([settings.start, settings.help, settings.form.get("terms"), settings.warehouse]):
        if not isinstance(page_conf, dict) or not idx == 0 and not page_conf.get("display"):
            continue
        label = page_conf.get("label")
        path = get_path(page_conf.get("path"), "pages")
        try:
            with open(path, "r") as f:  # open file
                LOGGER.debug(f"Reading {label} from content of {path}...")
                text = f.read()
        except FileNotFoundError:
            text = (
                f"<br>path:{path.name}<br> in config for page **{label}** does not exist."
                f"<br>Please review your config, read the logs and check /files."
                f"<br>If you started the program for the first time i may have fetched the page by now."
                f"<br>In that case a page reload might also fix the problem."
            )
        if text is not None:
            yield label, text
