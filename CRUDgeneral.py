# /Usuarios
from netmiko import ConnectHandler
import json

def get_users_all_routers():
    with open("routers.json", "r") as file:
        devices = json.load(file)
    users = {}
    for dev in devices:
        router = devices[dev]
        try:
            with ConnectHandler(**router) as connection:
                output = connection.send_command('show running-config | include username')
            output_lines = output.splitlines()
            user_dict = {}
            for line in output_lines:
                if line.startswith("username "):
                    parts = line.split()
                    username = parts[1]
                    privilege = parts[3]  # El privilegio se encuentra en la posición 3
                    password = parts[-1]
                    user_dict[username] = {'privilege': privilege, 'password': password}
            users[dev] = user_dict
        except:
            users[dev] = user_dict
    return users

def delete_user_all_routers(user):
    with open("routers.json", "r") as file:
        devices = json.load(file)
    user = str(user)
    for dev in devices:
        router = devices[dev]
        try:
            with ConnectHandler(**router) as connection:
                connection.send_config_set('no username ' + user)
                connection.save_config()
        except:
            print('No se pudo conectar al router ' + dev)
    return get_users_all_routers()

def create_user_all_routers(user, privileges, password):
    with open("routers.json", "r") as file:
        devices = json.load(file)
    user = str(user)
    privileges = str(privileges)
    password = str(password)
    for dev in devices:
        router = devices[dev]
        try:
            with ConnectHandler(**router) as connection:
                connection.send_config_set('username ' + user + ' privilege ' 
                                        + privileges + ' password ' + password)
                connection.save_config()
        except:
            print('No se pudo conectar al router ' + dev)
    return get_users_all_routers()

def update_user_all_routers(user, privileges=None, password=None):
    with open("routers.json", "r") as file:
        devices = json.load(file)
    user = str(user)
    if privileges is not None:
        privileges = str(privileges)
        comand = 'username ' + user + ' privilege ' + privileges
    if password is not None:
        password = str(password)
        comand = 'username ' + user + ' password ' + password
    if privileges is not None and password is not None:
        privileges = str(privileges)
        password = str(password)
        comand = 'username ' + user + ' privilege ' + privileges + ' password ' + password
    for dev in devices:
        router = devices[dev]
        try:
            with ConnectHandler(**router) as connection:
                connection.send_config_set(comand)
                connection.save_config()
        except:
            print('No se pudo conectar al router ' + dev)
    return get_users_all_routers()