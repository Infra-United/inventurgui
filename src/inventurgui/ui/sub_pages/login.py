import os
import time

from nicegui import ui, app
from inventurgui.ui.auth import create_jwt
from inventurgui.ui.layout import main_menu


def login_page():
    with ui.tab_panel('default').classes('m-0 w-full h-dvh text-secondary decoration-primary'):
        with ui.card().classes('mx-auto my-auto'):
            pw_in = ui.input('Password', password=True, password_toggle_button=True)
            ui.button('Log in', ).on('click', lambda:login(pw_in.value)).classes('mx-auto')

    async def login(password: str):
        if os.environ["UI_ADMIN_PASSWORD"] == password:
            token = create_jwt()
            app.storage.user.update({"auth_token": token})
            main_menu.refresh()
            ui.navigate.to("/")
        else:
            time.sleep(1)
            pw_in.set_value("")
            ui.notify("This password is incorrect.", color="negative")
