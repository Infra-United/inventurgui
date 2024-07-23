from getpass import GetPassWarning, getpass
from logging import debug, exception
import yaml
from functions.admin import hash_password

# Load from yaml file
# Here it is also possible to use PyYAML arguments, 
# for example to specify different loaders e.g. SafeLoader or FullLoader
# conf = Box.from_yaml(filename="./config.yaml", Loader=yaml.FullLoader) 


def load_config(config_file:str):
    debug(f"Loading config from {config_file}...")
    try:
        with open(config_file, 'r') as f: 
            config:dict = yaml.safe_load(f)
            if config is None:
                exception('Config is None.'), exit(1)
            else:
                debug(f"Successfully loaded the following config: \n {config}")
                return config
    except FileNotFoundError:
        exception('Config File not Found:', config_file); exit()
        
def dump_config(config_file:str, config:dict):
    debug(f"Dumping config to {config_file}...")
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
    except FileNotFoundError:
        exception('Config File not Found:', config_file); exit()
        
def set_password(config_file:str, config:dict):
    debug("Asking for a new password for the admin configuration page...")
    try: 
        config['admin']['hash'] = hash_password(getpass())
        dump_config(config_file, config)
        exit(0)
    except GetPassWarning:     
        print("Your Terminal is not able to prompt for passwords securely. Please use a standard Terminal like Unix bash."), exit(1)