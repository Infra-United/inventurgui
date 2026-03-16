from nicegui import ui, app

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.helper.magic_link import get_magic_link
from inventurgui.ui.helper.reusable_elements import back_fab
from inventurgui.ui.layout import drawer_menu


async def finish_page(warehouses:list[Warehouse]):
    ui.page_title(f"{settings.finish['label']}")
    with ui.tab_panel("finish").classes("w-full h-dvh m-0"):
        with ui.column(align_items="center").classes("mx-auto my-auto text-center items-center"):
            ui.html(f'<dotlottie-wc src="https://lottie.host/651035b0-fcbb-45cd-8117-cc6126920b25/wkhNl1xwcz.lottie" '
                    f'style="width: 300px;height: 300px" autoplay ></dotlottie-wc>', sanitize=False)
            md = ui.markdown().bind_content_from(Cache.form(), "finish", backward=lambda v: v if v else "")
            md.classes("pt-5 hyphens-none text-base/6 antialiasing text-gray-300 max-w-180") if md.content else None
            if Cache.form().get("delete"):
                return ui.timer(5, lambda: (app.storage.user.clear(), Cache(warehouses),
                                            drawer_menu.refresh(), ui.navigate.to("/")))
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
