import datetime
import re
from contextlib import suppress

from nicegui import app, ui, PageArguments
from nicegui.elements.checkbox import Checkbox
from nicegui.elements.date import Date
from nicegui.elements.drawer import LeftDrawer
from nicegui.elements.editor import Editor
from nicegui.elements.input import Input
from nicegui.observables import ObservableDict

from inventurgui.helper.config import config, EMAIL_REGEX, load_config, get_path
from inventurgui.helper.magic_link import load_data_from_magic_link
from inventurgui.helper.safe_url import url_safe
from inventurgui.helper.storage import Storage
from inventurgui.io.mail import send_mail
from inventurgui.io.request import save_request, delete_request, write_download_list
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import back_fab, tabs, tab_panels
from inventurgui.ui.markdown import render_markdown


async def form_page(ld: LeftDrawer, warehouses: list[Warehouse], args: PageArguments) -> None:
    form: dict[str, str | dict[str, str]] = load_config()["form"]

    ui.page_title(f"{form['label']}")
    def set_panel():
        if Storage.width() < 1280:
            form_panels.set_value(
                [t.props.get("label") for t in form_tabs.descendants()][0]
            )  # First tab is open by default
        else:
            form_panels.set_value("default")

    current_id = app.storage.browser["id"]
    request_id = args.query_parameters.get("id")
    if current_id != request_id:
        load_data_from_magic_link(current_id, request_id)

    ld.hide()
    terms = form.get("terms")
    form_tabs = tabs()
    form_panels = tab_panels(form_tabs)
    back_fab(config["cart"])
    with form_tabs.classes("xl:hidden"):
        with form_tabs:
            ui.tab(form.get("tab_label"), icon=form.get("tab_icon")).classes("px-7").props("inline-label")
            if terms.get("display"):
                ui.tab(terms.get("label"), icon=terms.get("icon")).props("inline-label")
    with form_panels:
        with ui.tab_panel("default").classes("xl:w-350 mx-auto p-5"):
            with ui.grid(columns=2) as grid:
                Form().create(warehouses)
                if terms.get("display"):
                    await render_markdown(form.get("terms"))
        with ui.tab_panel(form.get("tab_label")).classes("m-0"):
            Form().create(warehouses)
        if terms.get("display"):
            with ui.tab_panel(terms.get("label")).classes("m-0 p-0"):
                await render_markdown(form.get("terms"))
    set_panel()
    ui.on("resize", lambda: set_panel(), throttle=0.8, trailing_events=True)

class Form:
    def __init__(self):
        self.valid = False
        self.inputs: list[Input|Editor|Checkbox] = []
        self.config: dict[str, str | dict[str, str]] = load_config()["form"]
        self.dates: Date = ui.date()
        self.request: ObservableDict = Storage.form()

    def validate(self) -> None:
        self.valid = False
        with suppress(NameError):
            if any([not i.value for i in self.inputs]) or self.dates.value is None:
                self.valid = False
            else:
                self.valid = True

    async def submit(self, warehouses) -> None:
        is_update = True if self.request.get("sent") else False
        self.request.update({"finish": config.get("processing")})
        ui.navigate.to(f"/{url_safe(config['finish']['label'])}")
        self.request.update(
            {"sent": datetime.date.today().strftime(config["date_format"])}
            if not self.request.get("sent")
            else {"updated": datetime.date.today().strftime(config["date_format"])}
        )
        try:
            send_mail(self.request, warehouses, type="update" if is_update else "request")
            await save_request(self.request, warehouses)
            filename = get_path(f"lists/{config['finish'].get('filename')}-{self.request.get('name')}.ods")
            write_download_list(filename, warehouses)
            self.request.update({"download": str(filename)})
            self.request.update({"message": None})
            self.request.update({"finish": self.config.get("success")})
        except Exception as exception:
            self.request.update({"finish": self.config.get("failure")})
            send_mail(self.request, warehouses, type="failure", exception=exception)

    async def delete_request(self, warehouses:list[Warehouse]) -> None:
        ui.notify("Deleting...")
        self.request.update({"finish": self.config.get("processing")})
        ui.navigate.to(f"/{url_safe(config['finish']['label'])}")
        send_mail(self.request, warehouses, type="delete")
        await delete_request(self.request)
        ui.notify("Deleted")
        self.request.update({"deleted": True, "finish": self.config.get("deleted")})

    def create(self, warehouses:list[Warehouse]):
        with ui.dialog() as delete_dialog:
            with ui.card():
                ui.label("Bist du sicher?".upper()).classes("w-full pt-2 text-center tracking-widest")
                delete = ui.button(self.config.get("delete"), icon=self.config.get("delete_icon"), color="negative")
                delete.on_click(lambda: self.delete_request(warehouses))

        with ui.grid(columns=2).classes("w-full bg-dark pb-10 h-screen flex-column") as grid:
            with ui.column(align_items='end').classes("max-sm:col-span-2 ml-auto pb-10") as submit_column:
                submit = ui.button(self.config.get("send"), icon=self.config.get("send_icon"))
                submit.on_click(lambda: self.submit(warehouses))
                submit.props("text-color=secondary rounded")
                submit.classes("p-3 sm:w-80 text-lg")
                delete = ui.button(self.config.get("delete"), icon=self.config.get("delete_icon"),
                                   on_click=lambda: delete_dialog.open())
                delete.bind_visibility_from(self.request, "sent")
                delete.props("text-color=gray-300 rounded").classes("p-3 bg-negative sm:w-80 text-lg")

            with ui.column().classes("mx-auto max-sm:col-span-2") as column:
                dates_label = ui.label(f"{self.config.get('start')} - {self.config.get('end')}".upper()).classes(
                    "w-full pt-2 text-center tracking-widest"
                )
                dates = self.dates.classes("p-0").props("range minimal flat")
                dates.move(column)
                dates.props[":options"] = f'date => date >= "{datetime.date.today():%Y/%m/%d}"'
                dates.bind_value(self.request, "dates")
                dates.on_value_change(lambda: self.validate())

            email_validation = {self.config.get("email_invalid"): lambda v: True if re.match(EMAIL_REGEX, v) else False}
            input_validation = {self.config.get("please_fill"): lambda v: len(v) > 0}
            with ui.column().classes("items-stretch max-sm:col-span-2"):
                for key, value in self.config.get("input").items():
                    if not key == "message": # Negative if statement because editor has to be moved
                        i = ui.input(value, validation=email_validation if key == "email" else input_validation)
                        i.without_auto_validation()
                        i.on('blur', lambda x=i: x.validate())
                    else:
                        i = ui.editor(value='',
                            placeholder=self.config.get("message") if not self.request.get("sent")
                            else self.config.get("update_message")
                        )
                        i.classes("col-span-2")
                        i.move(grid) # Moves editor
                    if key == "name" or key == "email":
                        i.bind_enabled_from(self.request, "sent", backward=lambda v: not v)
                    i.on_value_change(lambda: self.validate())
                    i.bind_value(self.request, key)
                    self.inputs.append(i)

            with ui.column().classes("max-sm:col-span-2"):
                for value in self.config.get("checkbox").values():
                    c = ui.checkbox(value)
                    c.on_value_change(lambda: self.validate())
                    self.inputs.append(c)

            # Move so it is available as variable above
            submit_column.move(grid)
            submit.bind_enabled_from(self, 'valid')
            submit.bind_text_from(
                self.request, "sent",
                backward=lambda v: self.config.get("update") if v else self.config.get("send"))
            submit.bind_icon_from(
                self.request, "sent",
                backward=lambda v: self.config.get("update_icon") if v else self.config.get("send_icon")
            )