from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client, app, ui
from functions.users import get_users, hash_password, load_user_data

# unrestricted_page_routes: {'/login', '/'}

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages except the ones in $unrestricted_page_routes.

    It redirects the user to the login page if they are not authenticated.
    """
    
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False): # if user is not authenticated
            if request.url.path in Client.page_routes.values():
                if request.url.path not in {'/login', '/'}:
                   return RedirectResponse('/login') # go to login page
        elif request.url.path is not f"/{app.storage.user.get('username')}": # if a user tries to go to a page other than their own
            ui.notify('You are not allowed to access this page.', color='negative')
            return RedirectResponse(f"/{app.storage.user.get('username')}") # redirect to the users page 
        else:
            return RedirectResponse(f"/{app.storage.user.get('username')}") # redirect to the users page 
        return await call_next(request)

app.add_middleware(AuthMiddleware)

@ui.page('/login', dark=True)
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        user_data = load_user_data()
        if  user_data['admin']['username'] == username.value and user_data['admin']['password'] == hash_password(password.value):
            app.storage.user.update({'username': username.value, 'authenticated': True, 'admin': True})
            ui.navigate.to('/admin')
        elif app.storage.user['referrer_path'] == {'/settings'}: 
            ui.notify('You are not allowed to access this page - only admins can.', color='negative')
            return RedirectResponse('/')
        users = get_users(user_data)
        for user in users: # iterate through users to check if input matches a user
            if user.username == username.value and user.password == hash_password(password.value):
                app.storage.user.update({'username': username.value, 'authenticated': True})
                ui.navigate.to(f"/{username.value}")  # go to the users page 
            else:
                ui.notify('There is no Account with this username and password', color='negative')
    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    return None
        
    