from logging import debug
from sys import exception
from cli import args
from nicegui import ui, binding
from config.yaml import dump_yaml, load_yaml

# Methods to handle config from and to yaml file

config_file = args.config_file

def load_config() -> dict:
    debug(f"Loading config from {config_file}...")
    try:
        with open(config_file, 'r') as file:
            return load_yaml(file)      
    except FileNotFoundError:
        exception('File not Found:', config_file); exit()    
    
def dump_config(config:dict) -> None:
    debug(f"Dumping config to {config_file}...")
    try:
        with open(config_file, 'w') as file:
            dump_yaml(config.__dict__, file)
    except FileNotFoundError:
        exception('File not Found:', config_file); exit()    

config = load_config()

# Methods to handle Theme
class Theme:
    primary: binding.BindableProperty
    secondary: binding.BindableProperty
    dark: binding.BindableProperty
    
    def __init__(self):
        self.primary=config['theme']['primary']
        self.secondary=config['theme']['secondary']
        self.dark = True
        
    def set_colors(self):
        ui.colors(primary = self.primary, secondary = self.secondary).update()
        
    def set_primary_color(self, primary):
        self.primary = primary
        ui.colors(primary=self.primary).update()
    
    def set_secondary_color(self, secondary):
        self.secondary = secondary
        ui.colors(secondary=self.secondary).update()
        
    def toggle_dark(self, dark):
        self.dark = dark
        
theme = Theme()

