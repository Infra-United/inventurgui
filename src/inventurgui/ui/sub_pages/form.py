import datetime
import re
from contextlib import suppress

from nicegui import app, ui, PageArguments
from nicegui.elements.drawer import LeftDrawer
from nicegui.observables import ObservableDict

from inventurgui.helper.config import request_conf, config, EMAIL_REGEX, form
from inventurgui.io.mail import send_mail
from inventurgui.io.request import write_ods
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.layout import back_fab, tabs, tab_panels
from inventurgui.helper.magic_link import load_data_from_magic_link
from inventurgui.ui.markdown import render_markdown


async def form_page(ld:LeftDrawer, warehouses:list[Warehouse], args:PageArguments) -> None:
    def set_panel():
        if app.storage.user['screen'].get('width') < 1024:
            form_panels.set_value(
                [t.props.get('label') for t in form_tabs.descendants()][0])  # First tab is open by default
        else:
            form_panels.set_value('default')

    current_id = app.storage.browser['id']
    request_id = args.query_parameters.get('id')
    if current_id != request_id:
        load_data_from_magic_link(current_id, request_id)

    ld.hide()
    terms = request_conf.get('terms')
    form_tabs = tabs()
    form_panels = tab_panels(form_tabs)
    back_fab(config['cart'])
    with form_tabs.classes('lg:hidden'):
        with form_tabs:
            ui.tab(form.get('label'), icon=form.get('icon')).classes('px-7').props('inline-label')
            if terms.get('display'):
                ui.tab(terms.get('label'), icon=terms.get('icon')).props('inline-label')
        with form_panels:
            with ui.tab_panel('default').classes('xl:w-350 mx-auto p-5'):
                with ui.grid(columns=2) as grid:
                    create_form(warehouses)
                    if terms.get('display'):
                        await render_markdown(request_conf.get('terms'))
            with ui.tab_panel(form.get('label')).classes('m-0'):
                    create_form(warehouses)
            if terms.get('display'):
                with ui.tab_panel(terms.get('label')).classes('m-0 p-0'):
                    await render_markdown(request_conf.get('terms'))
    set_panel()
    ui.on('resize', lambda: set_panel(), throttle=0.8, trailing_events=True)


def create_form(warehouses:list[Warehouse]):
    def validate_form() -> bool:
        rules = [dates.value]
        [rules.append(i.value) for i in inputs]
        with suppress(NameError):
            for check in rules:
                if not check:
                    return False
        return True

    today:datetime.date = datetime.date.today()
    request:ObservableDict = app.storage.user.get('form')
    with ui.grid(columns=1).classes('w-full bg-dark h-screen') as grid:
        with ui.row().classes('pb-10') as row:
            ui.space()
            submit = ui.button(form.get('send'), icon=form.get('send_icon')).props('text-color=secondary rounded')
            submit.classes('p-3 sm:w-80 text-lg')

        dates = ui.date().classes('w-100 p-0 mx-auto').props('range minimal flat')
        dates.props[':options'] = f'date => date >= "{today:%Y/%m/%d}"'
        dates.bind_value(request, 'dates')
        dates.on_value_change(lambda: submit.enable() if value else submit.disable())

        inputs = []
        email_validation = {form.get('email_invalid'): lambda v: True if re.match(EMAIL_REGEX, v) else False}
        input_validation = {form.get('please_fill'): lambda v: len(v) > 0}
        for key, value in form.get('input').items():
            i = ui.input(value, validation=email_validation if key == 'email' else input_validation)
            if key == 'name' or key == 'email':
                i.bind_enabled_from(request, 'sent', backward=lambda v: not v)
            i.on_value_change(lambda s=submit: s.enable() if validate_form() else s.disable())
            i.bind_value(request, key).props('debounce=1000')
            inputs.append(i)

        dates_label = ui.label(f"{form.get('start')} - {form.get('end')}".upper()).classes(
            'w-full pt-2 text-center tracking-widest')
        dates.move(grid)

        ui.editor(placeholder=form.get('message')).bind_value(request, 'message')

        for value in form.get('checkbox').values():
            c = ui.checkbox(value)
            c.on_value_change(lambda s=submit: s.enable() if validate_form() else s.disable())
            inputs.append(c)

        row.move(grid)
        submit.disable()
        magic_link = f"https://{config['domain']}{ui.context.client.sub_pages_router.current_path}"
        update = {'sent': today.strftime(config['date_format'])} if not request.get('sent') else {'updated': today.strftime(config['date_format'])}
        submit.on_click(lambda: request.update(update))
        #submit.on_click(lambda: send_mail(request, warehouses, magic_link))
        submit.on_click(lambda: write_ods(request, warehouses))
        submit.on_click(lambda: request.update({'message': ''}))
        submit.bind_text_from(request, 'sent', backward=lambda v: form.get('update') if v else form.get('send'))
        submit.bind_icon_from(request, 'sent',
                              backward=lambda v: form.get('update_icon') if v else form.get('send_icon'))

