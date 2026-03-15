import datetime
import socket
import time
from contextlib import suppress

import nicegui.run
from nicegui import ui, app
from nicegui.elements.checkbox import Checkbox
from nicegui.elements.date import Date
from nicegui.elements.input import Input
from nicegui.observables import ObservableDict

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.paths import get_path
from inventurgui.io.cache import Cache
from inventurgui.io.exporter import save_request, delete_request, write_download_list
from inventurgui.io.mail import send_mail, RequestType
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.helper.magic_link import get_magic_link
from inventurgui.ui.helper.safe_url import url_safe
from inventurgui.ui.helper.validators import validate_mail, INPUT_VALIDATION
from inventurgui.ui.layout import warehouse_menu


class Form:
    def __init__(self):
        self.inputs: list[Input] = []
        self.checks: list[Checkbox] = []
        self.dates: Date = ui.date()
        self.request: ObservableDict = Cache.form()

    def validate(self) -> bool:
        with suppress(NameError):
            if any([not i.validate() for i in self.inputs]) or self.dates.value is None:
                return False
            elif any([not c.value for c in self.checks]):
                return False
            else:
                return True
        return False

    def create(self, warehouses:list[Warehouse]):
        with ui.dialog() as delete_dialog:
            with ui.card():
                ui.label(i18n.get("finish.are_you_sure").upper()).classes("w-full pt-2 text-center tracking-widest")
                delete = ui.button(icon='delete_sweep', color="negative")
                delete.on_click(lambda: send_delete(self.request, warehouses))

        with (ui.grid(columns=2).classes("w-full bg-dark pb-10 h-screen flex-column") as grid):
            with ui.row(align_items='end').classes("max-sm:col-span-2 ml-auto pb-10") as submit_column:
                delete = ui.button(icon="delete_sweep", on_click=lambda: delete_dialog.open())
                delete.bind_visibility_from(self.request, "request")
                delete.props("text-color=secondary rounded").classes("p-3 bg-red text-lg")
                submit = ui.button(icon="outgoing_mail")
                submit.on_click(lambda: submit_form(self.request, warehouses) if self.validate()
                                else ui.notify(i18n.get("form.invalid"), type='negative'))
                submit.props("text-color=secondary rounded")
                submit.classes("p-3 text-lg")

            with ui.column().classes("mx-auto max-sm:col-span-2") as column:
                dates_label = ui.label(f"{i18n.get('form.start')} - {i18n.get('form.end')}".upper())
                dates_label.classes("w-full pt-2 text-center tracking-widest")
                dates = self.dates.classes("p-0").props("range minimal flat")
                dates.move(column)
                dates.props[":options"] = f'date => date >= "{datetime.date.today():%Y/%m/%d}"'
                dates.bind_value(self.request, "dates")
                dates.on_value_change(lambda: self.validate())

            with ui.column().classes("items-stretch max-sm:col-span-2"):
                for key, value in settings.form.get("input").items():
                    i = ui.input(value, validation=(lambda v, k=key: validate_mail(k, v, self.request)) if key == "email" else INPUT_VALIDATION)
                    i.without_auto_validation()
                    i.on('blur', lambda x=i: x.validate())
                    if key == "name" or key == "email":
                        i.bind_enabled_from(self.request, "request", backward=lambda v: not v)
                    i.bind_value(self.request, key) if key != "email" else i.set_value(self.request.get(key))
                    self.inputs.append(i)
                if "message" in settings.form.keys():
                    e = ui.editor(value='',
                                  placeholder=i18n.get("form.message") if not self.request.get("sent")
                                  else i18n.get("form.update_message")
                                  )
                    e.classes("col-span-2")
                    e.bind_value(self.request, "message")
                    e.move(grid)  # Moves editor

            with ui.column().classes("max-sm:col-span-2"):
                if not self.request.get("request"):
                    for value in settings.form.get("checkbox").values():
                        c = ui.checkbox(value)
                        self.checks.append(c)

            # Move so it is available as variable above
            submit_column.move(grid)
            submit.bind_icon_from(
                self.request, "request",
                backward=lambda v: 'save' if v else 'outgoing_mail'
            )

async def submit_form(request: ObservableDict, warehouses: list[Warehouse]) -> None:
    is_update = True if request.get("request") else False
    request.update({"finish": i18n.get("finish.processing")})
    ui.navigate.to(f"/{url_safe(settings.finish['label'])}")
    magic_link = get_magic_link()
    request.update({"edit_link": magic_link})
    request.update(
        {"request": time.time()}
        if not request.get("request")
        else {"update": time.time()}
    )
    try:
        await save_request(request, warehouses)
        filename = get_path(f"{settings.organization}-{request.get('name')}.xlsx", "lists")
        await write_download_list(filename, warehouses)
        await nicegui.run.io_bound(lambda: send_mail(request,
                                                     request_type=RequestType.update if is_update else RequestType.request,
                                                     filename=filename,
                                                    ))
        request.update({"download": str(filename)})
        request.update({"finish": i18n.get("finish.success")})
    except Exception as exception:
        request.update({"finish": i18n.get("finish.failure_mail")})
        try:
            await nicegui.run.io_bound(
                lambda: send_mail(request, request_type=RequestType.failure, exception=exception))
            request.update({"finish": i18n.get("finish.failure_success")})
        except socket.gaierror as exception:
            request.update({"finish": i18n.get("finish.mail_exception")})
            LOGGER.exception("The mailserver is unreachable. Try again later.")


async def send_delete(request: ObservableDict, warehouses:list[Warehouse]) -> None:
    request.update({"finish": i18n.get("finish.processing")})
    ui.navigate.to(f"/{url_safe(settings.finish['label'])}")
    try:
        request.update({"delete": time.time()})
        await nicegui.run.io_bound(lambda: send_mail(request, RequestType.delete))
        await delete_request(request)
        request.update({"finish": i18n.get("finish.deleted"), "request": None})
        app.storage.user.clear()
        Cache(warehouses)
        warehouse_menu.refresh()
        request.update({"finish": i18n.get("finish.success")})
    except Exception as exception:
        request.update({"finish": i18n.get("finish.failure_mail")})
        try:
            await nicegui.run.io_bound(lambda: send_mail(request, request_type=RequestType.failure, exception=exception))
            request.update({"finish": i18n.get("finish.failure_success")})
        except socket.gaierror as exception:
            request.update({"finish": i18n.get("finish.mail_exception")})
            LOGGER.exception("The mailserver is unreachable. Try again later.")