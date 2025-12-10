from collections.abc import Callable
from pathlib import Path
from typing import Generator, Iterator, Hashable, Any, Coroutine

from nicegui import ui, app, run
from nicegui.elements.aggrid import AgGrid
from pandas import Series, DataFrame

from inventurgui.helper.config import config, get_path
from inventurgui.helper.logger import LOGGER
from inventurgui.io.warehouse import Warehouse
from inventurgui.ui.grid import create_aggrid
from inventurgui.ui.layout import tool_buttons


def get_selected(iterator:Callable[Iterator[tuple[Hashable, Series[Any]]]], row_ids:list[str]) -> DataFrame:
    def _match_selected() -> Generator[Series, None, None]:
        for row_id in row_ids:
            for i, row_data in iterator():
                if str(i) == row_id:
                    yield row_data
    return DataFrame.from_records([r for r in _match_selected()])

def get_df(w:Warehouse) -> Coroutine[Any, Any, DataFrame]:
    LOGGER.debug(f'Task started for {w.name}...')
    row_ids: list = list(app.storage.user.get(w.name))
    return run.cpu_bound(get_selected, w.inventory.iterrows, row_ids)

async def get_results(tasks:list[Coroutine[Any, Any, DataFrame]]):
    results = [await task for task in tasks]
    count = 0
    for result in results:
        df = result
        if not df.empty:
            count += 1
            name = df['warehouse'].unique()[0]
            yield count, name, df

async def truck_page(warehouses:list[Warehouse]) -> None:
    LOGGER.debug(f'Creating Cart page...')
    tasks = [get_df(w) for w in warehouses]

    ui.query(".nicegui-sub-pages").style(replace='gap:0')
    tabs = ui.tabs().classes('bg-dark lg:w-[calc(100vw-250px)] h-[56px] m-0 p-0').props(
            'height=56px flat active-bg-color=secondary active-color=primary mobile-arrows stretch')
    tab_panels = ui.tab_panels(tabs).classes('w-dvw')

    async for count, name, df in get_results(tasks):
        with tabs:
            with ui.tab(str(count)) as tab:
                with ui.row():
                    ui.icon(config['cart']['icon'], size='sm')
                    ui.label(name.upper())
                tab.classes('text-center w-full font-bold subpixel-antialiased tracking-widest')
                tab.props('inline-label')
                badge = ui.badge('0', text_color='dark').props("rounded floating")
                badge.bind_text_from(app.storage.user, name, lambda e: len(e))
        with tab_panels:
            with ui.tab_panel(str(count)).classes('m-0 p-0 w-full'):
                grid: AgGrid = create_aggrid(name, df, config, cart=True)
                tool_buttons(grid)
        tab_panels.set_value(str(1))
        tab.set_label('')
    #if not app.storage.user.get('notified')['truck']:
    ui.notify("Bitte passe die Stückzahlen an indem du darauf klickst.", position='center', timeout=3000, close_button=True, classes='')
    app.storage.user['notified']['truck'] = True
    LOGGER.info(f"Created grid for cart page")

def form_page():
    with ui.card().classes('w-screen h-screen p-0 m-0'):
        with ui.scroll_area().classes('h-[calc(100vh-52px)]'):
            request = Request()
            today = datetime.date.today()
            with ui.grid(columns=1).classes('xl:w-1/2 w-full p-3 max-sm:p-0'):
                name = ui.input(config['form']['name']).bind_value(request, 'name')
                place = ui.input(config['form']['place']).bind_value(request, 'place')
                start = ui.date_input(config['form']['start'], placeholder='DD.MM.YYYY').bind_value(request, 'start')
                start.picker.props[':options'] = f'date => date >= "{today:%Y/%m/%d}"'
                start.picker.props['mask'] = 'DD.MM.YYYY'
                end = ui.date_input(config['form']['end'], placeholder='DD.MM.YYYY').bind_value(request, 'end')
                end.picker.props[':options'] = f'date => date >= "{today:%Y/%m/%d}"'
                end.picker.props['mask'] = 'DD.MM.YYYY'
                email = ui.input(config['form']['email'], validation={'Not a valid email': lambda v: True if re.match(EMAIL_REGEX, v) else False})
                email.bind_value(request, 'email')
                email.on_value_change(lambda c: submit.enable() if c.value and email.validate() else submit.disable())
                donation = ui.input(config['form']['donation']).bind_value(request, 'donation')
                message = ui.editor(placeholder='Deine Mail an uns...')
                check = ui.checkbox(config['form']['checkbox']).bind_value(request, 'checkbox')
                check.on_value_change(lambda c: submit.enable() if c.value and email.validate() else submit.disable())
                submit = ui.button(config['form']['submit'])
                submit.disable()
                submit.on_click(lambda: Mail.send_mail(request.html, request.text, request.subject, request.email))


def help_page(help_file:Path = get_path(config['help']['path'])) -> None:
    # Create one Page for displaying help
    LOGGER.debug(f"Creating Help Panel with the content of {help_file}...")
    with ui.row().classes('w-screen p-2 m-0'):
        with open(help_file, 'r') as f:  # open file
            ui.markdown(f.read()).classes('pl-10 pb-20 m-0 text-base font-light text-secondary')

def category_page(category:str, warehouse: Warehouse) -> None:
    # Create One grid for each unique Category in the first Column
    LOGGER.debug(f'Creating Grid for {warehouse.name}/{category}...')
    category_data = warehouse.inventory[warehouse.inventory[config['data']['category']] == category]
    if category == config['everything']:
        category_data = warehouse.inventory
    grid:AgGrid = create_aggrid(warehouse.name, category_data, config)
    tool_buttons(grid)
    LOGGER.info(f"Created grid for: {warehouse.name}/{category}")
    # with ui.row():
    #   ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
    #  ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'link', True))
