from nicegui import ui
from nicegui.elements.markdown import Markdown

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path
from inventurgui.helper.logger import LOGGER

def render_markdown(text:str) -> Markdown:
    return ui.markdown(text).classes(
        "p-10 pt-5 mx-auto text-justify hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180"
    )

def read_markdown_files() -> dict[str, str]:
    markdown = {}

    def read_markdown(page_conf: dict[str, str]) -> None:
        if isinstance(page_conf, str) or not page_conf.get("display"):
            return
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
        markdown.update({label: text})

    for values in settings.start.values():
        read_markdown(values)
    read_markdown(settings.form.get("terms"))
    read_markdown(settings.warehouse)
    print(markdown)


    return markdown