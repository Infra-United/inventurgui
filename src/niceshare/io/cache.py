from nicegui import app
from nicegui.observables import ObservableList, ObservableDict

from niceshare.helper.i18n import i18n


class Cache:
    def __init__(self, warehouses):
        app.storage.user.indent = True
        app.storage.user.setdefault("Total", 0)
        app.storage.user.setdefault("width", 0)
        app.storage.user.setdefault(
            "form",
            {
                "dates": None,
                "name": "",
                "place": "",
                "donation": "",
                "email": "",
                "message": "",
                "messenger": "",
                "request": None,
                "update": None,
                "finish": None,
                "edit_link": None,
                "overlap": i18n.get("finish.no_overlap"),
            },
        )
        app.storage.user.setdefault("notified", None)
        app.storage.user.setdefault("added", [])
        app.storage.user.setdefault("deleted", [])
        app.storage.user.setdefault("edited", [])
        app.storage.user.setdefault("selected", [])
        app.storage.user.setdefault("show_lyrics", False)

    @classmethod
    def total(cls) -> int:
        return int(app.storage.user["Total"])

    @classmethod
    def width(cls) -> int:
        return int(app.storage.user["width"])

    @classmethod
    def set_width(cls, width: int):
        app.storage.user["width"] = width

    @classmethod
    def notified(cls) -> bool:
        return app.storage.user["notified"]

    @classmethod
    def form(cls) -> ObservableDict:
        return app.storage.user["form"]

    @classmethod
    def deleted(cls) -> ObservableList:
        return app.storage.user["deleted"]

    @classmethod
    def added(cls) -> ObservableList:
        return app.storage.user["added"]

    @classmethod
    def edited(cls) -> ObservableDict:
        return app.storage.user["edited"]

    @classmethod
    def selected(cls) -> ObservableList:
        return app.storage.user["selected"]

    @classmethod
    def show_lyrics(cls) -> bool:
        return app.storage.user["show_lyrics"]
