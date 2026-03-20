import datetime
import os

import jwt
from jwt import ExpiredSignatureError
from nicegui import Event

from inventurgui.io.cache import Cache

authenticated = Event[bool]()


def create_jwt():
    data = {
        "exp": datetime.datetime.now() + datetime.timedelta(hours=6),
    }
    return jwt.encode(data, os.environ["UI_AUTH_SECRET"], algorithm="HS256")


def authenticate_user() -> bool:
    try:
        if Cache.auth_token() is None:
            return False
        jwt.decode(Cache.auth_token(), os.environ["UI_AUTH_SECRET"], algorithms="HS256")
        return True
    except KeyError, ExpiredSignatureError:
        return False
