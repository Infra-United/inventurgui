import datetime
import re
from contextlib import suppress

from nicegui import app, ui
from nicegui.elements.drawer import LeftDrawer

from inventurgui.helper.config import request_conf, config, EMAIL_REGEX, form
from inventurgui.io.mail import send_mail
from inventurgui.io.request import write_ods
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import back_fab, tabs, tab_panels
from inventurgui.ui.markdown import render_markdown


async def form_page(ld:LeftDrawer, warehouses:list[Warehouse]) -> None:
    ld.hide()
    terms = request_conf.get('terms')
    form_tabs = tabs()
    form_panels = tab_panels(form_tabs)
    back_fab(config['cart'])
    with form_tabs:
        with form_tabs:
            ui.tab(form.get('label'), icon=form.get('icon')).classes('px-7').props('inline-label')
            ui.tab(terms.get('label'), icon=terms.get('icon')).props('inline-label')
        with form_panels:
            with ui.tab_panel(form.get('label')).classes('m-0'):
                    create_form(warehouses)
            with ui.tab_panel(terms.get('label')).classes('m-0 p-0'):
                await render_markdown(request_conf.get('terms'))
    form_panels.set_value([t.props.get('label') for t in form_tabs.descendants()][0]) # First tab is open by default


def create_form(warehouses:list[Warehouse]):
    def validate_form() -> bool:
        rules = [dates.value]
        [rules.append(i.validate()) for i in inputs]
        with suppress(NameError):
            [rules.append(c.value) for c in checks]
            for check in rules:
                if not check:
                    return False
        return True

    request = app.storage.user.get('form')
    with ui.grid(columns=1).classes('xl:w-1/2 w-full bg-dark h-screen lg:w-1/2') as grid:
        with ui.row().classes('pb-10') as row:
            ui.space()
            submit = ui.button(form.get('submit')).props('text-color=secondary rounded icon-right=send')
            submit.classes('p-3 sm:w-80 text-lg')
        #submit.on_click(lambda: send_mail(request, warehouses))
        submit.on_click(lambda: write_ods(request, warehouses))

        ui.label(f"{form.get('start')} - {form.get('end')}".upper()).classes(
            'w-full pt-2 text-center tracking-widest')
        dates = ui.date().classes('w-100 p-0 mx-auto').props('range minimal flat')
        dates.props[':options'] = f'date => date >= "{datetime.date.today():%Y/%m/%d}"'
        dates.bind_value(request, 'dates')
        dates.on_value_change(lambda: submit.enable() if value else submit.disable())

        inputs = []
        email_validation = {form.get('email_invalid'): lambda v: True if re.match(EMAIL_REGEX, v) else False}
        input_validation = {form.get('please_fill'): lambda v: len(v) > 0}
        for key, value in form.get('input').items():
            i = ui.input(value, validation=email_validation if key == 'email' else input_validation)
            i.on_value_change(lambda s=submit: s.enable() if validate_form() else s.disable())
            i.bind_value(request, key).props('debounce=1000')
            inputs.append(i)

        dates.move(grid)
        ui.editor(placeholder=form.get('message')).bind_value(request, 'message')

        checks = []
        for value in form.get('checkbox').values():
            c = ui.checkbox(value)
            c.on_value_change(lambda s=submit: s.enable() if validate_form() else s.disable())
            checks.append(c)

        row.move(grid)
        submit.disable()