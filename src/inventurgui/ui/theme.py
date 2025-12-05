from nicegui import binding, ui

from inventurgui.helper.config import config


# Methods to handle Theme
class Theme:
    primary: binding.BindableProperty
    secondary: binding.BindableProperty
    dark: binding.BindableProperty

    def __init__(self):
        self.primary = config['theme']['primary']
        self.secondary = config['theme']['secondary']
        self.dark = True

    def set_colors(self):
        ui.colors(primary=self.primary, secondary=self.secondary).update()

    def set_primary_color(self, primary):
        self.primary = primary
        ui.colors(primary=self.primary).update()

    def set_secondary_color(self, secondary):
        self.secondary = secondary
        ui.colors(secondary=self.secondary).update()

    def toggle_dark(self, dark):
        self.dark = dark

theme = Theme()