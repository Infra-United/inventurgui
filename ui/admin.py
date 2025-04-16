from nicegui import ui
from config.config import theme
from ui.auth import check_logout
from config.routers import user

lorem_ipsum:str = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

@user.page('/admin')
def admin():
   ui.query('.nicegui-content').classes('p-0')
   theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
   with ui.header().classes('fixed p-0 m-0 bg-secondary text-primary'):     
      with ui.tabs().classes('w-full') as tabs:
         theme_tab = ui.tab(name='theme_tab', label='Colors', icon='colorize')
         check_logout()
         
   with ui.card().classes('w-screen h-dvh p-0'):
      with ui.tab_panels(tabs, value=theme_tab).classes('w-full h-full p-0 fixed'):
         with ui.tab_panel(theme_tab):
            with ui.card().classes('md:w-1/2 w-full h-dvh bg-secondary text-base anitaliased text-primary') as background:
               text = ui.markdown(lorem_ipsum).classes('color-primary text-justify')
               with ui.row():
                  ui.color_input(label='Foreground Color', 
                                 on_change=lambda e: theme.set_primary_color(e.value)
                                 ).bind_value(text, 'text-color').classes('w-full md:w-auto xl:w-1/3 text-2xl font-bold')
                  ui.color_input(label='Background Color', 
                                 on_change=lambda e: theme.set_secondary_color(e.value),
                                 ).bind_value(background, 'bg-color'
                                 ).classes('w-full md:w-auto xl:w-1/3 text-2xl font-bold')
                  ui.space()
                  with ui.button('Save').classes('mt-3'):
                     ui.tooltip('Save your settings permanently.').classes('text-base bg-info')