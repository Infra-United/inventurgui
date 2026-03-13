import datetime
import re
from contextlib import suppress

from nicegui import ui, binding, app
from nicegui.elements.checkbox import Checkbox
from nicegui.elements.date import Date
from nicegui.elements.input import Input
from nicegui.observables import ObservableDict

from inventurgui.helper.config import settings, EMAIL_REGEX
from inventurgui.helper.i18n import i18n
from inventurgui.helper.paths import get_path
from inventurgui.ui.helper.safe_url import url_safe
from inventurgui.io.cache import Cache
from inventurgui.io.mail import send_mail
from inventurgui.io.request import save_request, delete_request, write_download_list
from inventurgui.io.warehouse import Warehouse


class Form:
    def __init__(self):
        self.valid: binding.BindableProperty = False
        self.inputs: list[Input] = []
        self.checks: list[Checkbox] = []
        self.dates: Date = ui.date()
        self.request: ObservableDict = Cache.form()

    def validate(self) -> None:
        self.valid = False
        with suppress(NameError):
            if any([not i.validate() for i in self.inputs]) or self.dates.value is None:
                self.valid = False
            elif any([not c.value for c in self.checks]):
                self.valid = False
            else:
                self.valid = True

    async def submit(self, warehouses) -> None:
        is_update = True if self.request.get("request") else False
        self.request.update({"finish": i18n.get("finish.processing")})
        ui.navigate.to(f"/{url_safe(settings.finish['label'])}")
        self.request.update(
            {"request": datetime.date.today().strftime(settings.date_format)}
            if not self.request.get("request")
            else {"update": datetime.date.today().strftime(settings.date_format)}
        )

        try:
            await save_request(self.request, warehouses)
            filename = get_path(f"{settings.organization}-{self.request.get('name')}.ods", "lists")
            write_download_list(filename, warehouses)
            send_mail(self.request, warehouses, request_type="update" if is_update else "request",  filename=filename)
            self.request.update({"download": str(filename)})
            self.request.update({"finish": i18n.get("finish.success")})
        except Exception as exception:
            self.request.update({"finish": i18n.get("finish.failure")})
            send_mail(self.request, warehouses, request_type="failure", exception=exception)

    async def delete_request(self, warehouses:list[Warehouse]) -> None:
        self.request.update({"finish": i18n.get("finish.processing")})
        ui.navigate.to(f"/{url_safe(settings.finish['label'])}")
        try:
            send_mail(self.request, warehouses, request_type="delete")
            await delete_request(self.request)
            self.request.clear()
            self.request.update({"delete": datetime.date.today().strftime(settings.date_format),
                                 "finish": i18n.get("finish.deleted"), "request": None})
            app.storage.user.clear()
        except Exception as exception:
            self.request.update({"finish": i18n.get("finish.failure")})
            send_mail(self.request, warehouses, request_type="failure", exception=exception)

    def create(self, warehouses:list[Warehouse]):
        with ui.dialog() as delete_dialog:
            with ui.card():
                ui.label(i18n.get("finish.are_you_sure").upper()).classes("w-full pt-2 text-center tracking-widest")
                delete = ui.button(icon='delete_sweep', color="negative")
                delete.on_click(lambda: self.delete_request(warehouses))

        with (ui.grid(columns=2).classes("w-full bg-dark pb-10 h-screen flex-column") as grid):
            with ui.row(align_items='end').classes("max-sm:col-span-2 ml-auto pb-10") as submit_column:
                delete = ui.button(icon="delete_sweep",
                                   on_click=lambda: delete_dialog.open())
                delete.bind_visibility_from(self.request, "request")
                delete.props("text-color=secondary rounded").classes("p-3 bg-red text-lg")
                submit = ui.button(icon="outgoing_mail")
                submit.on_click(lambda: self.submit(warehouses))
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

            email_validation = {i18n.get("form.email_invalid"): lambda v: True if re.match(EMAIL_REGEX, v) else False}
            input_validation = {i18n.get("form.please_fill_field"): lambda v: len(v) > 0}
            with ui.column().classes("items-stretch max-sm:col-span-2"):
                for key, value in settings.form.get("input").items():
                    i = ui.input(value, validation=email_validation if key == "email" else input_validation)
                    i.without_auto_validation()
                    i.on('blur', lambda x=i: x.validate())
                    if key == "name" or key == "email":
                        i.bind_enabled_from(self.request, "sent", backward=lambda v: not v)
                    i.on_value_change(lambda: self.validate())
                    i.bind_value(self.request, key)
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
                for value in settings.form.get("checkbox").values():
                    c = ui.checkbox(value)
                    c.on_value_change(lambda: self.validate())
                    self.checks.append(c)

            # Move so it is available as variable above
            submit_column.move(grid)
            submit.bind_enabled_from(self, 'valid')
            submit.bind_icon_from(
                self.request, "request",
                backward=lambda v: 'save' if v else 'outgoing_mail'
            )
            self.validate()