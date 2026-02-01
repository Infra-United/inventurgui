from nicegui import app, ui
from nicegui.observables import ObservableList, ObservableDict

class Storage:
    def __init__(self, warehouses):
        app.storage.user.indent = True
        app.storage.user.setdefault("screen", {})
        app.storage.user.setdefault("Total", 0)
        app.storage.user.setdefault("notified", False)
        app.storage.user.setdefault(
            "form", {"dates": None, "name": "", "place": "", "donation": "", "email": "", "message": "", "sent": None}
        )
        app.storage.user.setdefault("amounts", {})
        for warehouse in warehouses:
            app.storage.user.setdefault(warehouse.name, [])
            self.amounts().update({warehouse.name: {}}) if not self.amounts().get(warehouse.name) else None

    @classmethod
    def width(cls) -> int:
        return int(app.storage.user["screen"].get('width'))

    @classmethod
    def height(cls) -> int:
        return int(app.storage.user["screen"].get('height'))

    @classmethod
    def screen(cls) -> ObservableDict:
        return app.storage.user["screen"]

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
    def amounts(cls) -> ObservableDict:
        return app.storage.user["amounts"]

    @classmethod
    def selected(cls, name: str) -> ObservableList:
        return app.storage.user[name]

    @classmethod
    def auth_token(cls) -> str | None:
        return app.storage.user.get("auth_token")