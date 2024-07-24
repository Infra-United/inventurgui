from logging import debug
from sys import exception
from functions.cli import args
from functions.yaml import dump_yaml, load_yaml

# Load from yaml file
# Here it is also possible to use PyYAML arguments, 
# for example to specify different loaders e.g. SafeLoader or FullLoader

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