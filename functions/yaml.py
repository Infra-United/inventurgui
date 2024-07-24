from io import TextIOWrapper
from logging import debug, exception
import yaml

def load_yaml(stream:TextIOWrapper) -> dict:
    try:
        data:dict = yaml.load(stream, yaml.SafeLoader)
        debug(f"Successfully loaded the following data from yml: \n {data}")
        return data
    except yaml.YAMLError as exc:
        exception("Error in config file: \n" + exc), exit(1)
        
def dump_yaml(data:dict, stream:TextIOWrapper) -> None:
    try:
        yaml.dump(data, stream, yaml.SafeDumper)
        debug(f"Successfully dumped the following data to yml: \n {data}")
    except yaml.YAMLError as exc:
        exception("Error in config file: \n" + exc), exit(1)