import dataclasses
import html
from contextlib import suppress
from pathlib import Path
from typing import Generator, Protocol

from inventurgui.helper.logger import LOGGER


class MenuItem(Protocol):
    name: str

    @property
    def children(self) -> list[str]:...

@dataclasses.dataclass
class WikiChapter(MenuItem):
    name: str = None
    pages: list[str] = None

    @classmethod
    def create(cls, chapter_dict: dict[str, list[str]]) -> Generator[WikiChapter, None, None]:
        for name, pages in chapter_dict.items():
            yield WikiChapter(name=name, pages=pages)

    @property
    def children(self) -> list[str]:
        return self.pages

async def pull_wiki(url:str, file:Path):
    """try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        with open(path, "w+") as f:
            f.write(response.text)
    except httpx.HTTPError as e:
        LOGGER.warning(f"Error fetching {filename} from {url}: \n\nException:{e}\n\n")
    """


def read_wiki(path:Path) -> dict[str, str | dict[str,str] | list[WikiChapter]]:
    try:
        with (open(path, "r") as f):
            content = str(f.read())
            style = content[content.index("<style>"):content.index("</style>")] + "</style>"
            menu_start = content.index('<ul class="contents">')
            menu_end = content.index('<div class="page-break"></div>', menu_start)
            menu = parse_menu(content[menu_start:menu_end])
            pages = content[menu_end:-1].split('<div class="page-break"></div>')
            return {"style": fix_styles(style), "pages":get_page_ids(pages), "menu": menu}
    except FileNotFoundError:
        LOGGER.exception(f"File {path.name} not found.")
        raise FileNotFoundError


def fix_styles(style:str):
    style = style.replace("color:#222", f"color:#fff")
    style = style.replace("font-style:italic", "")
    style = style.replace("font-family:", "")
    style = style.replace("box-sizing:border-box;", "")
    return  style.replace("background-color:#f8f8f8", "background-color:#37474f")


def get_page_ids(pages:list[str]) -> dict[str, str]:
    pages_with_ids = {}
    for page in pages:
        with suppress(ValueError):
            start = page.index('>', page.index("id")) + 1
            page_id = (page[start:page.index('<', start)])
            pages_with_ids.update({page_id: html.unescape(page)})
    return pages_with_ids


def parse_menu(menu:str) -> list[WikiChapter]:
    """
    Parses the table of contents html-string to a string that can be evaluated to python objects.
    :param menu: The html-string containing the table of contents
    :return: the string that can be evaluated to a python object
    """
    menu_lines: list[str] = html.unescape(menu).splitlines()
    chapters:dict[str, list[str]] = {}
    chapter_name = ""
    for idx, line in enumerate(menu_lines):
        with suppress(ValueError):
            if line[line.index('#')+1:line.rindex('"')].startswith("chapter"):
                chapter_name = line.split(">")[-3].rstrip("</a")
                chapters.update({chapter_name: []})
            if line[line.index('#')+1:line.rindex('"')].startswith("page"):
                chapters.get(chapter_name).append(line.split(">")[-3].rstrip("</a"))
    return [i for i in WikiChapter.create(chapters)]