from base64 import b64encode
from getpass import GetPassWarning, getpass
import hashlib
from logging import debug, exception
import yaml

# Load from yaml file
# Here it is also possible to use PyYAML arguments, 
# for example to specify different loaders e.g. SafeLoader or FullLoader
# conf = Box.from_yaml(filename="./config.yaml", Loader=yaml.FullLoader) 

def load_config(config_file:str):
    debug(f"Loading config from {config_file}...")
    try:
        with open(config_file, 'r') as f: 
            CONFIG:dict = yaml.safe_load(f)
            debug(f"Successfully loaded the following config: \n {CONFIG}")
            return CONFIG
    except FileNotFoundError:
        exception('Config File not Found:', config_file); exit()
    except yaml.YAMLError as exc:
        print(exc), exit(1)
        
def dump_config(config_file:str, config):
    debug(f"Dumping config to {config_file}...")
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
    except FileNotFoundError:
        exception('Config File not Found:', config_file); exit()
    except yaml.YAMLError as exc:
        print(exc), exit(1)
        
def set_password(config_file:str, config:dict, password:str = None):
    debug("Asking for a new password for the admin configuration page...")
    try: 
        if password is not None:
            config['admin']['hash'] = hash_password(password)
        else: 
            config['admin']['hash'] = hash_password(getpass())
        dump_config(config_file, config)
        exit(0)
    except GetPassWarning:     
        print("Your Terminal is not able to prompt for passwords securely. Please use a standard Terminal like Unix bash."), exit(1)

def hash_password(password:str):
    encoded=(password).encode()
    result = hashlib.sha256(encoded)
    base = b64encode(result.digest()).decode('utf-8')[::-1]
    return base