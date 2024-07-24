from base64 import b64encode
from getpass import getpass
import hashlib
from sys import exception
from functions.yaml import load_yaml, dump_yaml
from functions.cli import args

users_file = args.users_file

class User:
    def __init__(self, id, username, password) -> None:
        self.id = id
        self.username = username
        self.password = password
        
def load_users():
    try:
        with open(users_file, 'r') as file:
            return load_yaml(file)
    except FileNotFoundError:
        exception('File not Found:', users_file); exit() 
"""
def get_users(users:list[dict] = [{}]):
    for count, user_yml in enumerate(users_data['Users']):
        user = count, user_yml['username'], user_yml['password'])
        users.append(user)
    return users
    
    dump_yaml(user_data, open_file(users_file, 'w'))
    # User Data needs to be reloaded for changes to apply
"""   
def set_password(user:User, password:str = None):
    print(f"Set a new password for {user.name}:")
    if password is not None:
        user.password = hash_password(password)
    if args.set_pass:
        user.password = hash_password(getpass())
    
def hash_password(password:str):
    encoded=(password).encode()
    result = hashlib.sha256(encoded)
    base = b64encode(result.digest()).decode('utf-8')[::-1]
    return base
