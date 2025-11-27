from io import TextIOWrapper
from logging import debug, exception
from pathlib import Path

import yaml

import inventurgui
from inventurgui.cli import ARGS
from nicegui import ui, binding

# Methods to handle helper from and to yaml file

def get_path(filename:str) -> Path:
    return Path(inventurgui.__file__).parent.parent.parent.joinpath(f"files/{filename}")

config_file: Path = get_path(ARGS.config_file)

def load_yaml(stream: TextIOWrapper) -> dict:
    try:
        data: dict = yaml.load(stream, yaml.SafeLoader)
        debug(f"Successfully loaded the following data from yml: \n {data}")
        return data
    except yaml.YAMLError as exc:
        exception("Error in helper file: \n" + exc), exit(1)


def dump_yaml(data: dict, stream: TextIOWrapper) -> None:
    try:
        yaml.dump(data, stream, yaml.SafeDumper)
        debug(f"Successfully dumped the following data to yml: \n {data}")
    except yaml.YAMLError as exc:
        exception("Error in helper file: \n" + exc), exit(1)

def load_config() -> dict:
    debug(f"Loading helper from {config_file}...")
    try:
        with open(config_file, 'r') as file:
            return load_yaml(file)      
    except FileNotFoundError:
        exception('File not Found:', config_file); exit()
    
def dump_config(config:dict) -> None:
    debug(f"Dumping helper to {config_file}...")
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

