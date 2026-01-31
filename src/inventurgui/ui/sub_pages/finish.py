from nicegui import ui, app

from inventurgui.helper.config import load_config
from inventurgui.helper.magic_link import get_magic_link
from inventurgui.helper.storage import Storage
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import checkout_fab, back_fab


async def finish_page(warehouses: list[Warehouse]):
    finish: dict[str, str | dict[str, str]] = load_config()["finish"]

    ui.page_title(f"{finish['label']}")
    with ui.tab_panel("finish").classes("w-full h-dvh m-0"):
        with ui.column(align_items="center").classes("mx-auto my-auto text-center"):
            md = ui.markdown("Test")
            md.bind_content_from(Storage.form(), "finish")
            md.classes("pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180")
            if Storage.form().get("deleted"):
                ui.timer(5, lambda: (app.storage.user.clear(), ui.navigate.to("/"), ui.navigate.reload()))
                return
            magic_link = get_magic_link()
            ui.link(magic_link, target=magic_link)
            ui.button(finish.get("copy_link"), icon="content_copy", on_click=ui.clipboard.write(magic_link))
            ui.markdown(finish.get("download_data")).classes(
                "pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180"
            )
            btn = ui.button(finish.get("download"), icon="download")
            btn.on_click(lambda: ui.download.file(Storage.form().get("download")))
            back_fab(load_config()["form"])
            checkout_fab(load_config()["start"])
