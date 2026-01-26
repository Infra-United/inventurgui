from nicegui import app

from inventurgui.main import frontend, backend

app.on_startup(backend)
frontend()
