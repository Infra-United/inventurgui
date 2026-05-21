import datetime
import socket
import time
from contextlib import suppress

from nicegui import ui
from nicegui.elements.checkbox import Checkbox
from nicegui.elements.date import Date
from nicegui.elements.input import Input
from nicegui.observables import ObservableDict
from slugify import slugify

from dataviewer.helper.config import settings
from dataviewer.helper.i18n import i18n
from dataviewer.helper.logger import LOGGER
from dataviewer.helper.paths import get_path
from dataviewer.io.cache import Cache
from dataviewer.io.excel import handle_request
from dataviewer.io.selection import Selection
from dataviewer.ui.helper.validators import INPUT_VALIDATION, validate_number


class Form:
    def __init__(self):
        self.inputs: list[Input] = []
        self.checks: list[Checkbox] = []
        self.dates: Date = ui.date()
        self.request: ObservableDict = Cache.form()

    def validate(self) -> bool:
        with suppress(NameError):
            if any([not i.validate() for i in self.inputs]):
                ui.notify(i18n.get("form.please_fill_field"))
                return False
            elif any([not c.value for c in self.checks]):
                ui.notify(i18n.get("form.please_check_boxes"))
                return False
            elif self.dates.value is None:
                ui.notify(i18n.get("form.please_provide_date"))
                return False
            else:
                return True
        return False

    def create(self, warehouses: list[Selection]):
        with ui.dialog() as delete_dialog:
            with ui.card():
                ui.label(i18n.get("finish.are_you_sure").upper()).classes("w-full pt-2 text-center tracking-widest")
                delete = ui.button(icon="delete_sweep", color="negative")
                delete.on_click(lambda: submit_form(self.request, warehouses, delete=True))

        with ui.grid(columns=2).classes("w-full bg-dark pb-10 h-screen flex-column") as grid:
            with ui.row(align_items="end").classes("max-sm:col-span-2 ml-auto pb-10") as submit_column:
                delete = ui.button(icon="delete_sweep", on_click=lambda: delete_dialog.open())
                delete.bind_visibility_from(self.request, "request")
                delete.props("text-color=secondary rounded").classes("p-3 bg-red text-lg")
                submit = ui.button(icon="outgoing_mail")
                submit.on_click(lambda: submit_form(self.request, warehouses) if self.validate() else None)
                submit.props("text-color=secondary rounded")
                submit.classes("p-3 text-lg")

            with ui.column().classes("max-sm:col-span-2") as column:
                dates_label = ui.label(f"{i18n.get('form.start')} - {i18n.get('form.end')}".upper())
                dates_label.classes("w-full pt-2 text-center tracking-widest")
                dates = self.dates.classes("w-full h-full p-0").props("range minimal flat")
                dates.move(column)
                dates.props[":options"] = f'date => date >= "{datetime.date.today():%Y/%m/%d}"'
                dates.bind_value(self.request, "dates")

            with ui.column().classes("items-stretch max-sm:col-span-2"):
                for key, value in settings.form.get("input").items():
                    i = ui.input(
                        value,
                        validation=(lambda v, k=key: validate_mail(k, v, self.request))
                        if key == "email"
                        else (lambda v, k=key: validate_number(k, v, self.request))
                        if key == "donation"
                        else INPUT_VALIDATION,
                    )
                    i.without_auto_validation()
                    i.on("blur", lambda x=i: x.validate())
                    if key == "name" or key == "email":
                        i.bind_enabled_from(self.request, "request", backward=lambda v: not v)
                    i.bind_value(self.request, key) if key != "email" else i.set_value(self.request.get(key))
                    self.inputs.append(i)
                if "message" in settings.form.keys():
                    e = ui.editor(
                        value="",
                        placeholder=i18n.get("form.message")
                        if not self.request.get("sent")
                        else i18n.get("form.update_message"),
                    )
                    e.classes("col-span-2")
                    e.bind_value(self.request, "message")
                    e.move(grid)  # Moves editor

            with ui.column().classes("max-sm:col-span-2 pb-10"):
                if not self.request.get("request"):
                    for value in settings.form.get("checkbox").values():
                        c = ui.checkbox(value)
                        self.checks.append(c)

            # Move so it is available as variable above
            submit_column.move(grid)
            submit.bind_icon_from(self.request, "request", backward=lambda v: "save" if v else "outgoing_mail")


async def submit_form(request: ObservableDict, warehouses: list[Selection], delete: bool = False) -> None:
    is_update = True if request.get("request") else False
    request.update({"finish": i18n.get("finish.processing")})
    ui.navigate.to(f"/{slugify(settings.finish['label'])}")
    magic_link = get_magic_link()
    request.update({"edit_link": magic_link})
    request.update(
        {"update": time.time()}
        if is_update and not delete
        else {"delete": time.time()}
        if delete
        else {"request": time.time()}
    )
    try:
        dl_path = get_path(f"{settings.organization}-{request.get('name')}.xlsx", "lists")
        await handle_request(request, warehouses, dl_path, delete)
        request.update({"download": str(dl_path)})
    except Exception as exception:
        request.update({"finish": i18n.get("finish.failure_mail")})
        try:
            LOGGER.exception(exception)
            request.update({"finish": i18n.get("finish.failure_success")})
        except socket.gaierror:
            request.update({"finish": i18n.get("finish.mail_exception")})
            LOGGER.exception("The mailserver is unreachable. Try again later.")
