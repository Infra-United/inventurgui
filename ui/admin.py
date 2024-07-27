from nicegui import binding, ui
from config.config import config

class Theme:
   primary = binding.BindableProperty()
   secondary = binding.BindableProperty()
   
   def __init__(self):
      self.primary=config['colors']['primary']
      self.secondary=config['colors']['secondary']
      self.dark = True

def color_setter(color):
   with ui.row().classes(f"{color} p-5") as row:
      ui.color_input(label='Color', value=color ,on_change=lambda e: row.style(f'color:{e.value}')).bind_value_from(row, 'color!important')

@ui.page('/admin', dark=True)
def admin():
   ui.query('.nicegui-content').classes('p-0')
   with ui.header().classes('fixed p-0 m-0 bg-secondary text-primary') as header:     
      with ui.tabs().classes('w-full') as tabs:
         theme_tab = ui.tab(name='theme_tab', label='Colors', icon='colorize').classes('')
   with ui.card().classes('w-screen h-dvh p-0'):
      with ui.tab_panels(tabs, value=theme_tab).classes('w-full h-full p-0 fixed'):
         with ui.tab_panel(theme_tab):         
            theme = Theme()
            ui.colors(primary = theme.primary, secondary = theme.secondary)
            with ui.card().classes('md:w-1/2 w-full h-dvh bg-black text-base anitaliased font-light text-secondary decoration-primary'):
              color_setter(theme.primary)
              color_setter(theme.secondary)