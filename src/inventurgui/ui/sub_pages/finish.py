from nicegui import ui, app

from inventurgui.helper.config import start, request_conf, finish
from inventurgui.helper.magic_link import get_magic_link
from inventurgui.ui.layout import checkout_fab, back_fab


def finish_page():
    with (ui.tab_panel('finish').classes('w-full h-dvh m-0')):
        with ui.column(align_items='center').classes('mx-auto my-auto text-center'):
            md = ui.markdown('Test')
            md.bind_content_from(app.storage.user.get('form'), 'finish')
            md.classes('pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180')
            magic_link = get_magic_link()
            ui.link(magic_link,target=magic_link)
            ui.button(finish.get('copy_link'), icon='content_copy', on_click=ui.clipboard.write(magic_link))
            back_fab(request_conf)
            checkout_fab(start)