from nicegui import ui, app

def selected_count_badge(warehouse_name:str):
    badge = ui.badge("0", color="primary", text_color="secondary").props().classes("text-bold ml-2")
    return badge.bind_text_from(app.storage.user.get("selected"), warehouse_name, backward=lambda v: str(len(v)))
