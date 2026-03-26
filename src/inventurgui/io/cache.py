from nicegui import app
from nicegui.observables import ObservableList, ObservableDict

from inventurgui.helper.i18n import i18n


class Cache:
    def __init__(self, warehouses):
        app.storage.user.indent = True
        app.storage.user.setdefault("Total", 0)
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
        app.storage.user.setdefault("selected", {})
        app.storage.user.setdefault("added", {})
        app.storage.user.setdefault("deleted", {})
        app.storage.user.setdefault("edited", {})
        app.storage.user.setdefault("amounts", {})
        app.storage.user.setdefault("weight", {})
        for warehouse in warehouses:
            app.storage.user["selected"].update({warehouse.name: []}) if not self.selected(warehouse.name) else None
            app.storage.user["added"].update({warehouse.name: []}) if not self.added(warehouse.name) else None
            app.storage.user["deleted"].update({warehouse.name: []}) if not self.deleted(warehouse.name) else None
            app.storage.user["edited"].update({warehouse.name: {}}) if not self.edited(warehouse.name) else None
            app.storage.user["amounts"].update({warehouse.name: {}}) if not self.amounts(warehouse.name) else None

    @classmethod
    def total(cls) -> int:
        return int(app.storage.user["Total"])

    @classmethod
    def notified(cls) -> bool:
        return app.storage.user["notified"]

    @classmethod
    def form(cls) -> ObservableDict:
        return app.storage.user["form"]

    @classmethod
    def amounts(cls, name: str) -> ObservableDict:
        return app.storage.user["amounts"].get(name)

    @classmethod
    def deleted(cls, name: str) -> ObservableList:
        return app.storage.user["deleted"].get(name)

    @classmethod
    def added(cls, name: str) -> ObservableList:
        return app.storage.user["added"].get(name)

    @classmethod
    def edited(cls, name: str) -> ObservableDict:
        return app.storage.user["edited"].get(name)

    @classmethod
    def selected(cls, name: str) -> ObservableList:
        return app.storage.user["selected"].get(name)

    @classmethod
    def weight(cls, name):
        return app.storage.user["weight"].get(name)

    @classmethod
    def set_weight(cls, name, weight: float):
        app.storage.user["weight"][name] = weight

    @classmethod
    def auth_token(cls) -> str | None:
        return app.storage.user.get("auth_token")
