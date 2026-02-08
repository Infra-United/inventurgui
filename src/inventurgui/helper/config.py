from logging import debug, exception
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource

import inventurgui
from inventurgui.cli import ARGS
from inventurgui.helper.logger import LOGGER

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


def get_path(filename: str) -> Path:
    return Path(inventurgui.__file__).parent.parent.parent.joinpath(f"files/{filename}")

config_file: Path = get_path(ARGS.config_file)
default_config_file: Path = get_path("default_config.yml")

# This is only for creating a default config if we cant find any
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=config_file,
       # yaml_config_section='',
        )
    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (YamlConfigSettingsSource(settings_cls),)

    title: str = 'InventurGui'
    favicon: str = 'logo.jpeg'
    domain: str = 'inventur.example.org'
    language: str = 'en'
    date_format: str = '%m/%d/%Y'
    theme: dict[str, str|bool] = {
            'primary': '#e89769',
            'secondary': '#37474f',
            'accent': '#607d8b',
            'dark_page': '#0d1626',
            'dark_mode': True
        }
    cloud: dict[str, str|dict[str, str]] = {
        'dir': "InventurGui",
        'pull': {
            'logo': 'logo.jpeg',
            'how_to': 'how_to.md',
            'help': 'help.md',
            'terms': 'terms.md',
            'about': 'about.md',
            'inventory': "inventory.ods"
        }
    }
    mail: dict[str, str] = {
        'subject_request': '[Request]',
        'subject_update': '[Update]',
        'subject_failure': '[Error]',
        'subject_delete': '[Delete]',
        'mail_to': 'hello@example.org',
        'admin': 'admin@example.org'
    }
    data:dict[str, str|int|dict[str, str]] = {
        'path': "inventory.ods",
        'sheets': 1,
        'columns': {
            'category': 'Category',
            'image': 'Image',
            'comment': 'Comment',
            'object': 'Name',
            'desc': 'Description',
            'weight': 'Weight',
            'total_weight': 'Total Weight',
            'count': 'Amount',
            'pack': 'Package',
        },
        'of_total': "of"  # String used in cart to format count as: "{value} {of_total} {total}"
    }
    @property
    def columns(self) -> dict[str, str]:
        return self.data['columns']
    start: dict[str, str|dict[str, str|bool]] = {
        'label': 'Start',
        'icon': 'home',
        'about': {
            'display': True,
            'label': 'About Us',
            'icon': 'info',
            'path': 'about.md',
        },
        'how_to': {
            'display': True,
            'label': 'How To',
            'icon': 'menu_book',
            'path': 'how_to.md',
        },
        'help': {
            'display': True,
            'label': 'Help',
            'icon': 'help_outline',
            'path': 'help.md',
        }
    }
    warehouse: dict[str, str] = {
        'label': 'Lager',
        'icon': 'warehouse',
        'path': 'lager.md',
        'everything': 'Everything',
        'selection': 'My Selection',
    }
    cart: dict[str, str] = {
        'label': 'Cart',
        'icon': 'cart',
        'tab_icon': 'local_shipping',
        'edit_tip': "Change the amounts to your needs by clicking on them.",
        'select_tip': "Please select something first.",
        'invalid_edit': "We don't have that many!",
    }
    form: dict[str, str|dict[str, str | bool]] = {
        'label': 'Form',  # The url path of the requests page
        'icon': 'article',  # The menu icon for the requests page
        'tab_label': 'Form',  # The label for the form tab on the page
        'tab_icon': 'article',  # The icon for the form tab on the page
        # Form Fields
        'input': {
            'name': 'Name', # This field is required
            'place': 'Ort',
            'donation': 'Donation',
            'email': 'E-Mail',
            'message': 'Your Message - Questions, Notes and important Infos'
        },
        'please_fill': 'Please fill this field.',
        # Just String Settings
        'email_invalid': 'This is not a valid email address.',
        'start': 'pick-up',
        'end': 'return',
        'month': 'month',
        'checkbox': {
            'terms': 'I have read the terms.'
        },
        # Submit Button Settings
        'send': 'Send',
        'update': 'Save',
        'delete': 'Delete',
        'send_icon': 'outgoing_mail',
        'update_icon': 'save',
        'delete_icon': 'delete_sweep',
        'sent': "Sent",
        'updated': "Updated",
        'update_link': "Editing link",
        'processing': "We are processing your request - please wait a moment...",
        'success': "Your request has been processed successfully - we will reach out to you soon. You can edit you request using this link:",
        'failure': "Something went wrong :/ We have been sent an error report - we will reach out to you soon.",
        'deleted': "Your request has been deleted. See you soon!",
        'terms': {  # Show terms to the user in a tab next to the form
            'display': True,  # Set this to false if you don't need this
            'label': 'Terms',
            'icon': 'policy',
            'path': 'terms.md',
        },
    }
    finish: dict[str, str] = {
        'label': 'Finish',
        'copy_link': 'Copy Link',
        'download': 'Download List',
        'filename': 'Org',
        'download_data': 'You can download a list with your request here:',
    }
    admin: dict[str, str] = {
        'edits': "My Changes",
        'upload': "Upload Image",
        'save': "Save",
    }
    requests: dict[str, str] = { # Only visible for admins and editors
        'label': 'Requests',
        'icon': 'drafts',
    }

def load_config() -> dict:
    debug(f"Loading config from {config_file}...")
    try:
        with open(config_file, "r") as file:
            return yaml.load(file, yaml.SafeLoader)
    except FileNotFoundError:
        exception("File not Found:", config_file), exit(1)
    except yaml.YAMLError as e:
        exception("Error in config file: \n" + e.args[0]), file.close(), exit(1)

def dump_config(config: dict) -> None:
    debug(f"Dumping config to {config_file}...")
    try:
        with open(config_file, "w") as file:
            yaml.dump(config.__dict__, file, yaml.SafeDumper)
    except FileNotFoundError:
        exception("File not Found:", config_file), exit(1)
    except yaml.YAMLError as e:
        exception("Error in config: \n" + e.args[0]), file.close(), exit(1)

def create_default_config() -> None:
    LOGGER.debug(f"Dumping default config to {default_config_file}...")
    if default_config_file.is_file():
        default_config_file.unlink()
    with open(default_config_file, 'w') as file:
        file.write(yaml.dump(Settings().model_dump(), Dumper=yaml.SafeDumper, sort_keys=False))
    LOGGER.info(f"Successfully wrote default config to {default_config_file}.")

settings = Settings(**load_config())