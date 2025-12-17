import os

from nicegui import json, app

from inventurgui.helper.config import get_path

def load_data_from_magic_link(old_id:str, new_id:str) -> None:
    with open(get_path(f'/users/storage-user-{new_id}.json'), 'r') as f:
        app.storage.user.update(json.loads(f.read()))
        app.storage.browser.update({'id': new_id})