import datetime
import re
from contextlib import suppress

from nicegui import app, ui, PageArguments
from nicegui.elements.drawer import LeftDrawer
from nicegui.observables import ObservableDict

from inventurgui.helper.config import config, EMAIL_REGEX, load_config, get_path
from inventurgui.helper.magic_link import load_data_from_magic_link
from inventurgui.helper.safe_url import url_safe
from inventurgui.io.mail import send_mail
from inventurgui.io.request import save_request, delete_request, write_download_list
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import back_fab, tabs, tab_panels
from inventurgui.ui.markdown import render_markdown


async def form_page(ld: LeftDrawer, warehouses: list[Warehouse], args: PageArguments) -> None:
    form: dict[str, str | dict[str, str]] = load_config()["form"]

    def set_panel():
        if app.storage.user["screen"].get("width") < 1280:
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
                create_form(warehouses)
                if terms.get("display"):
                    await render_markdown(form.get("terms"))
        with ui.tab_panel(form.get("tab_label")).classes("m-0"):
            create_form(warehouses)
        if terms.get("display"):
            with ui.tab_panel(terms.get("label")).classes("m-0 p-0"):
                await render_markdown(form.get("terms"))
    set_panel()
    ui.on("resize", lambda: set_panel(), throttle=0.8, trailing_events=True)


def create_form(warehouses: list[Warehouse]):
    form: dict[str, str | dict[str, str]] = load_config()["form"]

    def validate_form() -> bool:
        rules = [dates.value]
        [rules.append(i.value) for i in inputs]
        with suppress(NameError):
            for check in rules:
                if not check:
                    return False
        return True

    async def handle_submit():
        is_update = True if request.get("sent") else False
        request.update({"finish": form.get("processing")})
        ui.navigate.to(f"/{url_safe(config['finish']['label'])}")
        request.update(
            {"sent": today.strftime(config["date_format"])}
            if not request.get("sent")
            else {"updated": today.strftime(config["date_format"])}
        )
        try:
            send_mail(request, warehouses, type="update" if is_update else "request")
            await save_request(request, warehouses)
            filename = get_path(f"lists/{form.get('filename')}-{request.get('name')}.ods")
            await write_download_list(filename, warehouses)
            request.update({"download": str(filename)})
            request.update({"message": None})
            request.update({"finish": form.get("success")})
        except Exception as exception:
            request.update({"finish": form.get("failure")})
            send_mail(request, warehouses, type="failure", exception=exception)

    async def handle_delete():
        ui.notify("Deleting...")
        request.update({"finish": form.get("processing")})
        ui.navigate.to(f"/{url_safe(config['finish']['label'])}")
        send_mail(request, warehouses, type="delete")
        await delete_request(request)
        ui.notify("Deleted")
        request.update({"deleted": True, "finish": form.get("deleted")})

    today: datetime.date = datetime.date.today()
    request: ObservableDict = app.storage.user.get("form")
    with ui.dialog() as delete_dialog:
        with ui.card():
            ui.label("Bist du sicher?".upper()).classes("w-full pt-2 text-center tracking-widest")
            ui.button(form.get("delete"), icon=form.get("delete_icon"), color="negative", on_click=handle_delete)
    with ui.grid(columns=2).classes("w-full bg-dark pb-10 h-screen flex-column") as grid:
        with ui.column().classes("ml-auto pb-20") as submit_column:
            submit = ui.button(form.get("send"), icon=form.get("send_icon"), on_click=handle_submit)
            submit.props("text-color=secondary rounded")
            submit.classes("p-3 sm:w-80 text-lg")
            delete = ui.button(form.get("delete"), icon=form.get("delete_icon"), on_click=lambda: delete_dialog.open())
            delete.bind_visibility_from(request, "sent")
            delete.props("text-color=gray-300 rounded").classes("p-3 bg-negative sm:w-80 text-lg")

        with ui.column().classes("mx-auto max-sm:col-span-2"):
            dates_label = ui.label(f"{form.get('start')} - {form.get('end')}".upper()).classes(
                "w-full pt-2 text-center tracking-widest"
            )
            dates = ui.date().classes("p-0").props("range minimal flat")
            dates.props[":options"] = f'date => date >= "{today:%Y/%m/%d}"'
            dates.bind_value(request, "dates")
            dates.on_value_change(lambda: submit.enable() if value else submit.disable())

        inputs = []
        email_validation = {form.get("email_invalid"): lambda v: True if re.match(EMAIL_REGEX, v) else False}
        input_validation = {form.get("please_fill"): lambda v: len(v) > 0}
        with ui.column().classes("items-stretch max-sm:col-span-2"):
            for key, value in form.get("input").items():
                if not key == "message":
                    i = ui.input(value, validation=email_validation if key == "email" else input_validation)
                else:
                    i = ui.editor(
                        placeholder=form.get("message") if not request.get("sent") else form.get("update_message")
                    )
                    i.classes("col-span-2")
                    i.move(grid)
                if key == "name" or key == "email":
                    i.bind_enabled_from(request, "sent", backward=lambda v: not v)
                i.on_value_change(lambda s=submit: s.enable() if validate_form() else s.disable())
                i.bind_value(request, key).props("debounce=1000")
                inputs.append(i)

        with ui.column().classes("pb-20"):
            for value in form.get("checkbox").values():
                c = ui.checkbox(value)
                c.on_value_change(lambda s=submit: s.enable() if validate_form() else s.disable())
                inputs.append(c)

        # Move so it is available as variable above
        submit_column.move(grid)
        submit.disable()
        submit.bind_text_from(request, "sent", backward=lambda v: form.get("update") if v else form.get("send"))
        submit.bind_icon_from(
            request, "sent", backward=lambda v: form.get("update_icon") if v else form.get("send_icon")
        )
