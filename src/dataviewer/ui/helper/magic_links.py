from nicegui import json, app, ui
from slugify import slugify

from dataviewer.helper.config import settings
from dataviewer.helper.paths import get_path


def get_magic_link() -> str:
    return f"{settings.domain}/{slugify(settings.cart['label'])}?id={app.storage.browser['id']}"


def load_data_from_magic_link(new_id: str) -> None:
    try:
        with open(get_path(f"storage-user-{new_id}.json", "users"), "r") as f:
            app.storage.user.update(json.loads(f.read()))
            app.storage.browser.update({"id": new_id})
            ui.navigate.reload()
    except FileNotFoundError:
        ui.notify(f"Sorry, couldn't find data for =id?{new_id}.", type="negative", position="center", text="secondary")
        ui.timer(5, lambda: ui.navigate.to("/"), once=True)
