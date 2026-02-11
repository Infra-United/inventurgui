# Ensure directory structure
from os import mkdir
from pathlib import Path
from typing import Literal

import inventurgui

dirs = ["users", "images", "locales", "lists", "pages"]

def ensure_dirs(warehouse_names:list[str]):
    for d in dirs:
        d = get_path(d)
        if not d.exists():
            mkdir(d)
        if d == "images":
            for w in warehouse_names:
                w_dir = get_path(w, "images")
                if not w_dir.is_dir():
                    mkdir(w_dir)

def get_path(filename: str, subdir: Literal["users", "images", "locales", "lists", "pages"] = None) -> Path:
    if subdir is not None:
        return Path(inventurgui.__file__).parent.parent.parent.joinpath(f"files/{subdir}/{filename}")
    else:
        return Path(inventurgui.__file__).parent.parent.parent.joinpath(f"files/{filename}")


