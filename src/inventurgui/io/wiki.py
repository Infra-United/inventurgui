import dataclasses
from typing import Generator, Protocol, Tuple, override

import httpx
from bs4 import BeautifulSoup
from slugify import slugify

from inventurgui.helper.config import settings
from inventurgui.helper.images import cache_image, match_img_url
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path

WIKI_ROOT = slugify(settings.help["label"])


class MenuItem(Protocol):
    name: str

    @property
    def children(self) -> list[str]: ...

    @property
    def routes(self) -> dict[str, str]: ...

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


def pull_wiki():
    file = get_path(settings.help["path"], "pages")
    url = settings.help["url"]
    try:
        response = httpx.Client().get(url)
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
            return Wiki(style=fix_styles(str(soup.style)), root=home_page, menu=wiki_menu, content=pages)
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
            chapter_name: str = item.string
            item['href'] = f"/{WIKI_ROOT}/{slugify(f"{item.string}-{item['href'].split("-")[-1]}")}"
            menu.update({item.string: {item.string: item['href']}})
        else:
            page_name = f"{item.string}-{item['href'].split("-")[-1]}"
            item['href'] = f"/{WIKI_ROOT}/{slugify(chapter_name)}/{slugify(page_name)}"
            menu[chapter_name].update({item.string: item['href']})
    return soup.prettify(), [i for i in WikiChapter.create(menu)]

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
    page_id = 0
    for idx, page in enumerate(pages[1:]):
        page = page.replace("background-color:#f1c40f", "background-color:#607d8b")
        page = page.replace("background-color:rgb(241,196,15)", "background-color:#607d8b")
        soup = BeautifulSoup(page, "html.parser")

        # Cache images
        images = soup.find_all('img')
        for i, img in enumerate(images):
            if not img:
                continue
            if img.parent.get("href"): # If there is a URL in <a href="">
                link = img.parent.get("href")
            else: # If there is a URL in <img src="">
                link = img["src"]
            url_dict: dict | None = match_img_url(link)
            if not url_dict: # Don't handle Base64 Strings for now
                continue
            filename = link.split("/")[-1].split("-")[0]
            img_url = await cache_image(url_dict, "wiki", filename, thumbnail_size=800)
            img.parent['href'] = img_url
            img['src'] = img_url

        # Extract chapter and page ids for routes
        h1 = soup.find('h1')
        if h1.get('id').startswith("chapter"):
            chapter_id = h1.get('id').split("-")[-1]
            page_dict.update({chapter_id: {chapter_id: pages[0] if idx == 0 else soup.prettify()}})
        elif h1.get('id').startswith("page"):
            page_id = h1.get('id').split("-")[-1]
            page_dict.get(chapter_id).update({page_id: soup.prettify()})

    return [i for i in WikiChapter.create(page_dict)]
