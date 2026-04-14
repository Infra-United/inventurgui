import dataclasses
from contextlib import suppress
from typing import Generator, Protocol, Tuple, override

import httpx
from bs4 import BeautifulSoup
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.images import cache_image, match_img_url, cache_base64_img
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path

WIKI_ROOT = slugify(settings.help["label"])


class MenuItem(Protocol):
    name: str

    @property
    def children(self) -> list[str]: ...

    @property
    def routes(self) -> dict[str, str]: ...


def þroperty(args):
    pass


@dataclasses.dataclass
class Wiki:
    style: str
    root: str
    menu: list[WikiChapter]
    content: list[WikiChapter]

@dataclasses.dataclass
class WikiChapter(MenuItem):
    name: str = None
    pages: dict[str, str] = None

    @classmethod
    def create(cls, chapter_dict: dict[str, dict[str, str]]) -> Generator[WikiChapter, None, None]:
        for name, pages in chapter_dict.items():
            yield WikiChapter(name=name, pages=pages)

    @override
    @property
    def children(self) -> list[str]:
        return list(self.pages.keys())

    @override
    @property
    def routes(self) -> dict[str, str]:
        return self.pages


async def pull_wiki():
    file = get_path(settings.help["path"], "pages")
    url = settings.help["url"]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=120)
        with open(file, "w+") as f:
            f.write(response.text)
    except httpx.HTTPError as e:
        LOGGER.warning(f"Error fetching {file.name} from {url}: \n\nException:{e}\n\n")


async def read_wiki() -> Wiki:
    file = get_path(settings.help["path"], "pages")
    try:
        with open(file, "r") as f:
            content = str(f.read())
            soup = BeautifulSoup(content, "html.parser")
            pages = content[content.index("<div") : -1].split('<div class="page-break"></div>')
            home_page, wiki_menu = parse_home(pages[0])
            pages = await parse_pages(pages)
            menu = [c for c in clean_menu(wiki_menu, pages)]
            return Wiki(style=fix_styles(str(soup.style)), root=home_page, menu=menu, content=pages)
    except FileNotFoundError:
        LOGGER.exception(f"File {file.name} not found.")
        raise FileNotFoundError


def parse_home(home: str) -> Tuple[str, list[WikiChapter]]:
    home = home.replace("4.8em", "") #TODO
    soup = BeautifulSoup(home, "html.parser")
    toc = soup.find('ul', class_="contents")
    menu: dict[str, dict[str, str]] = {}
    for item in toc.find_all('a'):
        if item['href'].startswith("#chapter"):
            chapter_name: str = str(item.string)
            item['href'] = f"/{WIKI_ROOT}/{slugify(f"{item.string}-{item['href'].split("-")[-1]}")}"
            menu.update({item.string: {item.string: str(item['href'])}})
        else:
            page_name = f"{item.string}-{item['href'].split("-")[-1]}"
            item['href'] = f"/{WIKI_ROOT}/{slugify(chapter_name)}/{slugify(page_name)}"
            menu[chapter_name].update({str(item.string): str(item['href'])})
    return soup.prettify(), [i for i in WikiChapter.create(menu)]

def clean_menu(menu: list[WikiChapter], content: list[WikiChapter]) -> Generator[WikiChapter, None, None]:
    for idx, chapter in enumerate(menu):
        with suppress(IndexError):
            pages = content[idx].pages
        for name, route in chapter.pages.copy().items():
            page = pages.get(route.split('-')[-1])
            if not page:
                chapter.pages.pop(name)
        yield chapter

def fix_styles(style: str):
    style = style.replace("--color-link: #206ea7", f"--color-link: {settings.theme.get('links')}")
    style = style.replace("color:#222", "color:#fff")
    style = style.replace("font-style:italic", "")
    style = style.replace("font-family:", "")
    style = style.replace("box-sizing:border-box;", "")
    return style.replace("background-color:#f8f8f8", "background-color:#37474f")


async def parse_pages(pages: list[str]) -> list[WikiChapter]:
    """
    Parses the table of contents from a list of page-html-strings.
    :param pages: The list of html-strings containing the pages
    :return: a list of WikiChapters
    """
    page_dict: dict[str, dict[str, str]] = {}
    chapter_id = 0
    for idx, page in enumerate(pages[1:]):
        page = page.replace("background-color:#f1c40f", "background-color:#607d8b")
        page = page.replace("background-color:rgb(241,196,15)", "background-color:#607d8b")
        soup = BeautifulSoup(page, "html.parser")

        # Cache images
        images = soup.find_all('img')
        for i, img in enumerate(images):
            if not img:
                continue
            if href:=img.parent.get("href"): # If there is a URL in <a href="">
                link = str(href)
            else: # If there is a URL in <img src="">
                link = str(img["src"])
            url_dict: dict | None = match_img_url(link)
            if url_dict:
                filename = link.split("/")[-1].split("-")[0]
                img_url = await cache_image(url_dict, "wiki", filename, thumbnail_size=800)
            else: # Don't handle Base64 Strings for now
                filename = str(img["src"][-30:])
                img_url = await cache_base64_img(str(img["src"]), "wiki", filename, thumbnail_size=800)
            img.parent['href'] = img_url
            img['src'] = img_url

        # Extract chapter and page ids for routes
        h1 = soup.find('h1')
        # noinspection PyUnresolvedReferences
        if h1.get('id').startswith("chapter"):
            # noinspection PyUnresolvedReferences
            chapter_id = h1.get('id').split("-")[-1]
            if len(soup.find_all(limit=5)) > 4:
                page_dict.update({chapter_id: {chapter_id: pages[0] if idx == 0 else soup.prettify()}})
            else:
                page_dict.update({chapter_id: {}})
        elif h1.get('id').startswith("page"):
            # noinspection PyUnresolvedReferences
            page_id = h1.get('id').split("-")[-1]
            page_dict[str(chapter_id)].update({page_id: soup.prettify()})

    return [i for i in WikiChapter.create(page_dict)]
