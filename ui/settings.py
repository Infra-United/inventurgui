from nicegui import ui

@ui.page('/admin', dark=True)
def settings():
   ui.label("Settings Page")
   
   # TODO implement gui to change settings