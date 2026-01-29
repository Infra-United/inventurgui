import datetime
import os
import jwt
from nicegui import app, Event
from starlette.responses import RedirectResponse

authenticated = Event[bool]()

def create_jwt():
    data = {
        "exp": datetime.datetime.now() + datetime.timedelta(hours=6),
    }
    return jwt.encode(data, os.environ["UI_STORAGE_SECRET"], algorithm="HS256")

def authenticate_user() -> bool:
    try:
        jwt.decode(app.storage.user["auth_token"], os.environ["UI_STORAGE_SECRET"], algorithms="HS256")
        return True
    except KeyError:
        return False

def logout():
    app.storage.browser.update({"auth_token": None})
    RedirectResponse("/", status_code=200)