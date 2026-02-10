from nicegui import ui, app

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.magic_link import get_magic_link
from inventurgui.io.cache import Cache
from inventurgui.ui.layout import checkout_fab, back_fab


async def finish_page():
    ui.page_title(f"{settings.finish['label']}")
    with ui.tab_panel("finish").classes("w-full h-dvh m-0"):
        with ui.column(align_items="center").classes("mx-auto my-auto text-center"):
            md = ui.markdown("Test")
            md.bind_content_from(Cache.form(), "finish")
            md.classes("pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180")
            if Cache.form().get("deleted"):
                ui.timer(5, lambda: (app.storage.user.clear(), ui.navigate.to("/"), ui.navigate.reload()))
                return
            magic_link = get_magic_link()
            ui.label(f"{i18n.get("finish.editing_link")}:".upper()).classes("w-full antialiasing text-base/6 tracking-wider")
            ui.link(magic_link, target=magic_link)
            ui.button(i18n.get("finish.copy_link"), icon="content_copy", on_click=ui.clipboard.write(magic_link))
            ui.markdown(i18n.get("finish.download_tip")).classes(
                "pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180"
            )
            btn = ui.button(i18n.get("finish.download_button"), icon="download")
            btn.on_click(lambda: ui.download.file(Cache.form().get("download")))
            back_fab(settings.form)
