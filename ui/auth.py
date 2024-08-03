from logging import debug
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client, app, ui
from config.config import theme
from config.users import get_users, hash_password, load_user_data



class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages except login and / (index).
    It redirects the user to the login page if they are not authenticated.
    """
    
    async def dispatch(self, request: Request, call_next) -> Optional[RedirectResponse]:
        # if user is not authenticated redirect them to login page
        user_authenticated = app.storage.user.get('authenticated', False)
        user_username = app.storage.user.get('username')
        path = request.url.path
        if path in Client.page_routes.values():
            debug(path)
            if not user_authenticated:
                debug('User not authenticated')
                if path not in {'/login', '/'}:
                    debug('Redirecting to /login')
                    return RedirectResponse('/login') # go to login page
            else:
                debug('User is authenticated')
                # if a user tries to go to a page other than their own and is not admin => redirect them to their own page 
                if path != f"/{user_username}":
                    debug('User tries to go to page other than their own')
                    if user_username != "admin":
                        debug('User is not "admin"')
                        return RedirectResponse(f"/{user_username}") # redirect to the users page
        return await call_next(request)

app.add_middleware(AuthMiddleware)

@ui.page('/login')
def login():
    theme.set_colors(), ui.dark_mode(theme.dark, on_change=lambda e: theme.toggle_dark(e.value))
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        user_data = load_user_data()
        users = get_users(user_data)
        if users is not None:
            for user in users: # iterate through users to check if input matches a user
                if user.username == username.value and user.password == hash_password(password.value):
                    app.storage.user.update({'username': username.value, 'authenticated': True})
                    ui.navigate.to(f"/{username.value}")  # go to the users page 
                else:
                    ui.notify('There is no Account with this username and password', color='negative')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    
def check_logout():
    if app.storage.user.get('authenticated', False):
        def try_logout():
            app.storage.user.update({'authenticated': False})
        with ui.button(on_click=try_logout()):
            ui.tab(name='logout', label='Logout', icon='logout')
            