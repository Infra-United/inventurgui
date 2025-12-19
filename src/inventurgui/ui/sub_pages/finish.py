import tempfile
import uuid

from nicegui import ui, app

from inventurgui.helper.config import get_path, load_config
from inventurgui.helper.magic_link import get_magic_link
from inventurgui.io.request import write_download_list
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import checkout_fab, back_fab


async def finish_page(warehouses:list[Warehouse]):
    finish: dict[str, str | dict[str, str]] = load_config()['finish']
    with (ui.tab_panel('finish').classes('w-full h-dvh m-0')):
        with ui.column(align_items='center').classes('mx-auto my-auto text-center'):
            md = ui.markdown('Test')
            md.bind_content_from(app.storage.user.get('form'), 'finish')
            md.classes('pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180')
            magic_link = get_magic_link()
            ui.link(magic_link,target=magic_link)
            ui.button(finish.get('copy_link'), icon='content_copy', on_click=ui.clipboard.write(magic_link))
            ui.markdown(finish.get('download_data')).classes('pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180')
            btn = ui.button(finish.get('download'), icon='download')
            filename = get_path(f"lists/{finish.get('filename')}-{app.storage.user['form'].get('name')}.ods")
            await write_download_list(filename, warehouses)
            btn.on_click(lambda: ui.download.file(filename))
            back_fab(load_config()['request'])
            checkout_fab(load_config()['start'])
