from nicegui import json, app, ui

from inventurgui.helper.config import get_path, settings
from inventurgui.helper.safe_url import url_safe


def get_magic_link() -> str:
    return f"https://{settings['domain']}/{url_safe(settings['cart']['label'])}?id={app.storage.browser['id']}"


def load_data_from_magic_link(old_id: str, new_id: str) -> None:
    try:
        with open(get_path(f"/users/storage-user-{new_id}.json"), "r") as f:
            app.storage.user.update(json.loads(f.read()))
            app.storage.browser.update({"id": new_id})
            ui.navigate.reload()
    except FileNotFoundError:
        ui.notify(f"Sorry, couldn't find data for =id?{new_id}.", type="negative", position="center", text="secondary")
        ui.timer(5, lambda: ui.navigate.to("/"), once=True)
