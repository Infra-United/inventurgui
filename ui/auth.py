from logging import debug
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import Client, app, ui
from config.config import theme
from config.users import get_users, load_user_data, User, write_user_data
from config import routers

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages except try_login and / (index).
    It redirects the user to the try_login page if they are not authenticated.
    """
    
    async def dispatch(self, request: Request, call_next) -> Optional[RedirectResponse]:
        # if user is not authenticated redirect them to try_login page
        user_data = load_user_data()
        users = get_users(user_data)
        path = request.url.path
        if path in Client.page_routes.values():
            debug(path)
            if path != "/":    
                for user in users:
                    if f"{routers.user.prefix}/{user.username}" == path:
                        if user.authenticated == True:
                            debug('User is authenticated')
                        else:
                            debug('User is not authenticated')
                            return RedirectResponse("/")
                    else: # if a user tries to go to a page other than their own and is not admin => redirect them to their own page 
                        debug('User tries to go to page other than their own')
                        return RedirectResponse(f"{routers.user.prefix}/{user.username}") # redirect to the users page
        return await call_next(request)

app.add_middleware(AuthMiddleware)

def try_login(username: str, password: str):
    user_data = load_user_data()
    users = get_users(user_data)
    if users is not None:
        for user in users: 
            # iterate through users to check if input matches a user
            if user.username == username and user.password == password:
                user.authenticated == True
                ui.navigate.to(f"{routers.user.prefix}/{username}")  # go to the users page
            else:
                ui.notify("This username and password does not match any registered user.", color='negative')
                return False
            
def register(username:str, password:str):
        user_data = load_user_data()
        users = get_users(user_data)
        user = User(id=users.count(User)+1, username=username, password=password)
        users.append(user); write_user_data(users)
        ui.navigate.to(f"/{routers.user.prefix}/{username}")
    
def check_logout():
    if app.storage.user.get('authenticated', False):
        def try_logout():
            app.storage.user.update({'authenticated': False})
            ui.navigate.to("/")
        with ui.button(on_click=try_logout()):
            ui.tab(name='logout', label='Logout', icon='logout')
            