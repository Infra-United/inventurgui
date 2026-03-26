from nicegui import ui, app

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.io.cache import Cache
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.helper.magic_link import get_magic_link
from inventurgui.ui.helper.reusable_elements import back_fab
from inventurgui.ui.layout import drawer_menu


async def finish_page(warehouses: list[Warehouse]):
    ui.page_title(f"{settings.finish['label']}")
    with ui.tab_panel("finish").classes("w-full h-dvh m-0"):
        with ui.column(align_items="center").classes("mx-auto my-auto text-center items-center"):
            ui.html(
                '<dotlottie-wc src="https://lottie.host/651035b0-fcbb-45cd-8117-cc6126920b25/wkhNl1xwcz.lottie" '
                'style="width: 250px; height: 250px" autoplay ></dotlottie-wc>',
                sanitize=False,
            )
            classes = "pt-5 hyphens-none text-base/6 antialiasing max-w-180"
            finish = ui.markdown().bind_content_from(Cache.form(), "finish", backward=lambda v: v if v else "")
            finish.classes(classes) if finish.content else None
            ui.markdown().bind_content_from(Cache.form(), "overlap").classes(f"{classes} text-primary")
            if Cache.form().get("delete"):
                ui.notify(i18n.get("finish.deleted"), position='center', color="primary", textColor="dark")
                app.storage.user.clear()
                Cache(warehouses)
                drawer_menu.refresh()
                ui.navigate.to("/")
            else:
                magic_link = get_magic_link()
                ui.label(f"{i18n.get('finish.editing_link')}:".upper()).classes(
                    "w-full antialiasing text-base/3 tracking-wider"
                )
                ui.label(i18n.get('finish.editing_link_tip')).classes(classes)
                ui.link(magic_link, target=magic_link).classes(classes).classes("text-primary")
                ui.markdown(i18n.get("finish.download_tip")).classes(classes)
                btn = ui.button(i18n.get("finish.download_button"), icon="download").classes("bg-secondary")
                btn.on_click(lambda: ui.download.file(Cache.form().get("download")))
                back_fab(settings.form)
