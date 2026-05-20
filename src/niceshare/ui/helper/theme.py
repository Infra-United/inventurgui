from typing import Self

from nicegui import ui

from niceshare.helper.config import settings


# Methods to handle Theme
class Theme:
    instance = None

    def __init__(self, config: dict[str, str]) -> None:
        self.primary = config.get("primary")
        self.secondary = config.get("secondary")
        self.accent = config.get("accent")
        self.dark_page = config.get("dark_page")
        self.links = config.get("links")
        self.dark_mode = config.get("dark_mode")

    @classmethod
    def singleton(cls) -> Self:
        if not cls.instance:
            cls.instance = Theme(config=settings.theme)
        return cls.instance

    def set_colors(self):
        ui.colors(
            primary=self.primary,
            secondary=self.secondary,
            accent=self.accent,
            dark_page=self.dark_page,
            links=self.links,
        ).update()
        ui.dark_mode(self.dark_mode)
