from nicegui import binding, ui

# Methods to handle Theme
class Theme:
    primary: binding.BindableProperty
    secondary: binding.BindableProperty
    dark: binding.BindableProperty

    def __init__(self, config:dict[str, str]) -> None:
        self.primary = config.get('primary')
        self.secondary = config.get('secondary')
        self.accent = config.get('accent')
        self.dark_page = config.get('dark_page')
        self.dark_mode = config.get('dark_mode')

    def set_colors(self):
        ui.colors(primary=self.primary,
                  secondary=self.secondary,
                  accent=self.accent,
                  dark_page=self.dark_page,
                  ).update()

    def set_primary_color(self, primary):
        self.primary = primary
        ui.colors(primary=self.primary).update()

    def set_secondary_color(self, secondary):
        self.secondary = secondary
        ui.colors(secondary=self.secondary).update()

    def toggle_dark(self, dark_mode):
        self.dark_mode = dark_mode