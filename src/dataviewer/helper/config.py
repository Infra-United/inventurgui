from logging import debug, exception, warning
from pathlib import Path
from typing import Self

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource

from dataviewer.cli import ARGS
from dataviewer.helper.logger import LOGGER
from dataviewer.helper.paths import get_path

config_file: Path = get_path(ARGS.config_file)
default_config_file: Path = get_path("default_config.yml")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=config_file,
        # yaml_config_section='',
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (YamlConfigSettingsSource(settings_cls),)

    title: str = "InventurGui"
    logo: str = "logo.png"
    favicon: str = "favicon.png"
    organization: str = "example"
    domain: str = "https://inventur.example.org"
    port: int = 8080
    language: str = "en"
    locale: str = "en_US.UTF-8"
    date_format: str = "%m/%d/%Y"
    time_format: str = "%H:%M"
    theme: dict[str, str | bool] = {
        "primary": "#e89769",
        "secondary": "#37474f",
        "accent": "#607d8b",
        "dark_page": "#0d1626",
        "dark_mode": True,
    }
    dav: dict[str, str | float | dict[str, str]] = {
        "dir": "InventurGui",
        "refresh_interval_hours": 24,
        "pull": {
            "logo": "logo.jpeg",
            "help": "help.md",
            "terms": "terms.md",
            "start": "start.md",
            "inventory": "inventory.ods",
        },
    }

    @property
    def refresh_timer(self) -> float:
        return self.dav["refresh_interval_hours"] * 3600

    data: dict[str, str | int | list[str] | dict[str, str]] = {
        "filename": "inventory",
        "warehouses": [""],
        "columns": {
            "category": "Selection",
            "title": "title",
            "tone": "tone",
            "chord": "chord",
            "lyrics": "lyrics",
            "desc": "description",
            "dance": "dance_description",
            "url": "link"
        },
    }

    @property
    def columns(self) -> dict[str, str]:
        return self.data["columns"]

    @property
    def data_filename(self) -> str:
        return self.data["filename"]

    start: dict[str, str | bool] = {"label": "Start", "icon": "home", "path": "about.md"}
    help: dict[str, str | bool] = {
        "display": True,
        "wiki": False,
        "label": "Help",
        "icon": "help_outline",
        "path": "help.md",
    }
    selection: dict[str, str | bool] = {
        "label": "Selection",
        "display": True,
        "icon": "warehouse",
        "path": "lager.md",
        "everything": "Everything",
        "selection": "My Selection",
    }
    cart: dict[str, str] = {
        "label": "Cart",
        "icon": "cart",
        "tab_icon": "local_shipping",
    }
    form: dict[str, str | dict[str, str | bool]] = {
        "label": "Form",  # The url path of the requests page
        "icon": "article",  # The menu icon for the requests page
        "tab_label": "Form",  # The label for the form tab on the page
        "tab_icon": "article",  # The icon for the form tab on the page
        # Form Fields
        "from": "Pick-Up",
        "to": "Return",
        "input": {
            "name": "Name",  # This field is required
            "place": "Ort",
            "donation": "Donation",
            "messenger": "Messenger-Contact (Signal, etc.)",
        },
        "message": "Your Message - Questions, Notes and important Infos",
        "checkbox": {"terms": "I have read the terms."},
        "terms": {  # Show terms to the user in a tab next to the form
            "display": True,  # Set this to false if you don't need this
            "label": "Terms",
            "icon": "policy",
            "path": "terms.md",
        },
    }
    finish: dict[str, str] = {"label": "Finish"}
    requests: dict[str, str] = {  # Only visible for admins and editors
        "label": "Requests",
        "icon": "drafts",
        "filename": "requests",
    }

    @classmethod
    def load_config(cls) -> Self:
        debug(f"Loading config from {config_file}...")
        try:
            with open(config_file, "r") as file:
                return Settings(**yaml.load(file, yaml.SafeLoader))
        except FileNotFoundError:
            warning("File not Found - Loading default-config:", config_file)
        except yaml.YAMLError as e:
            exception("Error in config file: \n" + e.args[0]), file.close()
        with open(default_config_file, "r") as file:
            return Settings(**yaml.load(file, yaml.SafeLoader))

    def dump_config(self) -> None:
        debug(f"Dumping config to {config_file}...")
        try:
            with open(config_file, "w") as file:
                yaml.dump(self.model_dump(), file, yaml.SafeDumper)
        except FileNotFoundError:
            exception("File not Found:", config_file), exit(1)
        except yaml.YAMLError as e:
            exception("Error in config: \n" + e.args[0]), file.close(), exit(1)

    @classmethod
    def create_default_config(cls) -> None:
        LOGGER.debug(f"Dumping default config to {default_config_file}...")
        if default_config_file.is_file():
            default_config_file.unlink()
        with open(default_config_file, "w") as file:
            file.write(yaml.dump(Settings().model_dump(), Dumper=yaml.SafeDumper, sort_keys=False))
        LOGGER.info(f"Successfully wrote default config to {default_config_file}.")


if not config_file.is_file():
    Settings.create_default_config()
    print(f"Please copy {default_config_file} to {config_file} and edit it to your needs!")
    exit(0)
settings = Settings.load_config()
