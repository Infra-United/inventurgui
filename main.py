from nicegui import ui
from functions.admin import admin
from functions.cli import get_args
from functions.config import hash_password, load_config, set_password
from functions.data import get_ods_data
from functions.main_ui import create_main_ui

@ui.page('/')
def main():
    data = get_ods_data(config['data']['path'])
    create_main_ui(config, data)
    
@ui.page('/login', dark=True)
def login():
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        if  config['admin']['username'] == username.value and config['admin']['password_hash'] == hash_password(password.value):
            ui.navigate.to('/admin')
        else:
            ui.notify('Wrong username or password', color='negative')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    
if __name__ in {"__main__", "__mp_main__"}:
    args:dict = get_args()                          # get Arguments from Command-Line and set log-level
    config:dict = load_config(args.config_file)     # get Config from yml file
    if args.set_pass:                               # set a new password if option is specified in commandline     
        set_password(args.config_file, config)
    main()
    
