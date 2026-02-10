# Ensure directory structure
from os import mkdir
from pathlib import Path

import inventurgui
from inventurgui.cli import ARGS


def ensure_dirs():
    dirs = ["users", "images", "locales", "lists"]
    for d in dirs:
        d = get_path(d)
        if not d.exists():
            mkdir(d)

def get_path(filename: str) -> Path:
    return Path(inventurgui.__file__).parent.parent.parent.joinpath(f"files/{filename}")


config_file: Path = get_path(ARGS.config_file)
default_config_file: Path = get_path("default_config.yml")
