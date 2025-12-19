from nicegui import ui, app
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import load_config
from inventurgui.ui.markdown import render_markdown


async def warehouse_page(ld:LeftDrawer):
    warehouse_conf: dict = load_config()["warehouse"]
    ui.page_title(warehouse_conf.get('label'))
    ld.show()
    await render_markdown(warehouse_conf)
    props: str = f"text-color=secondary"
    with ui.page_sticky(position='bottom-right', x_offset=18, y_offset=18).classes('z-999'):
        fab = ui.fab(icon='navigate_next', direction='up').props(f"{props} active-icon='hourglass_top'")
        fab.on('click', lambda: ld.show())
        fab.on('mouseenter', lambda: label.set_visibility(True), throttle=0.2)
        fab.on('mouseleave', lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot('label'):
            with ui.row():
                icon = ui.icon(warehouse_conf.get('icon'))
                label = ui.label(warehouse_conf.get('label')).classes('text-secondary text-base')
                label.set_visibility(False)
            badge = ui.badge('0', color='primary', text_color='secondary').props(
                "rounded floating").classes('text-bold')
            badge.bind_text_from(app.storage.user, 'total')
            badge.bind_visibility_from(app.storage.user, 'total', backward=lambda v: v > 0)