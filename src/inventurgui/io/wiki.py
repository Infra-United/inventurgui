import dataclasses
import html
from contextlib import suppress
from pathlib import Path
from typing import Generator, Protocol

import httpx
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.logger import LOGGER

WIKI_ROOT = WIKI_ROOT = slugify(settings.help['label'])

class MenuItem(Protocol):
    name: str

    @property
    def children(self) -> list[str]:...

@dataclasses.dataclass
class WikiChapter(MenuItem):
    name: str = None
    pages: dict[str, str] = None

    @classmethod
    def create(cls, chapter_dict: dict[str, dict[str, str]]) -> Generator[WikiChapter, None, None]:
        for name, pages in chapter_dict.items():
            yield WikiChapter(name=name, pages=pages)

    @property
    def children(self) -> list[str]:
        return list(self.pages.keys())

async def pull_wiki(url:str, file:Path):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        with open(file, "w+") as f:
            f.write(response.text)
    except httpx.HTTPError as e:
        LOGGER.warning(f"Error fetching {file.name} from {url}: \n\nException:{e}\n\n")

def read_wiki(path:Path) -> dict[str, str | list[WikiChapter]]:
    try:
        with (open(path, "r") as f):
            content = str(f.read())
            style = content[content.index("<style>"):content.index("</style>")] + "</style>"
            pages = content[content.index("<div"):-1].split('<div class="page-break"></div>')
            pages[0] =  wiki_home(pages[0])
            return {'style': fix_styles(style), 'root':pages[0] , 'chapters': parse_menu(pages)}
    except FileNotFoundError:
        LOGGER.exception(f"File {path.name} not found.")
        raise FileNotFoundError

def wiki_home(home:str) -> str:
    home = home.replace("4.8em", "")
    menu_start = home.index('ul class="contents">')
    menu_lines = home[menu_start:].splitlines()
    for idx, line in enumerate(menu_lines):
        with suppress(ValueError, IndexError):
            to_replace = line[line.index("#"):line.rindex('"')]
            if to_replace.startswith("#chapter"):
                chapter_slug = slugify(line.split(">")[-3].rstrip("</a"))
                replacement = f"/{WIKI_ROOT}/{chapter_slug}"
            elif to_replace.startswith("#page"):
                replacement = f"/{WIKI_ROOT}/{chapter_slug}/{slugify(line.split(">")[-3].rstrip("</a"))}"
            else:
                continue
            menu_lines[idx] = line.replace(to_replace, replacement)
    #home = home.replace(home[menu_start:-1], "\n".join(menu_lines))
    home = home[:menu_start-1]
    return home

def fix_styles(style:str):
    style = style.replace("color:#222", f"color:#fff")
    style = style.replace("font-style:italic", "")
    style = style.replace("font-family:", "")
    style = style.replace("box-sizing:border-box;", "")
    return  style.replace("background-color:#f8f8f8", "background-color:#37474f")


def parse_menu(pages:list[str]) -> list[WikiChapter]:
    """
    Parses the table of contents from a list of page-html-strings.
    :param pages: The list of html-strings containing the pages
    :return: a list of WikiChapters
    """
    chapters:dict[str, dict[str, str]] = {}
    chapter_name = ""
    for idx, page in enumerate(pages[1:-1]):
        page = page.replace("background-color:#f1c40f", f"background-color:#607d8b")
        page = page.replace("background-color:rgb(241,196,15)", f"background-color:#607d8b")
        id_line = html.unescape(page[page.index('<h1 id="') + 8: page.index('</h1')])
        if id_line.startswith("chapter"):
            chapter_name = id_line.split(">")[-1].rstrip("</h1")
            chapters.update({chapter_name: {chapter_name: pages[0] if idx == 0 else page}})
        if id_line.startswith("page"):
            page_name = id_line.split(">")[-1].rstrip("</h1")
            chapters.get(chapter_name).update({page_name: page})
    return [i for i in WikiChapter.create(chapters)]