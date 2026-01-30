from nicegui import app

def width():
    return app.storage.user["screen"].get('width')