from netmiko import ConnectHandler
import json

def get_users(host):
    with open("routers.json", "r") as file:
        devices = json.load(file)
    users = {}
    for dev in devices:
        if devices[dev]['ip'] == host or dev == host:
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
                        privilege = parts[3]
                        password = parts[-1]
                        user_dict[username] = {'privilege': privilege, 'password': password}
                users[dev] = user_dict
            except:
                return {'status': 'No hay conexion al router'}
            break
    return users

def delete_user(host, user):
    with open("routers.json", "r") as file:
        devices = json.load(file)
    user = str(user)
    for dev in devices:
        if devices[dev]['ip'] == host or dev == host:
            router = devices[dev]
            try:
                with ConnectHandler(**router) as connection:
                    connection.send_config_set('no username ' + user)
                    connection.save_config()
                break
            except:
                return {'status': 'No hay conexion al router'}
    return get_users(host)

def create_user(host, user, privileges, password):
    with open("routers.json", "r") as file:
        devices = json.load(file)
    user = str(user)
    privileges = str(privileges)
    password = str(password)
    for dev in devices:
        if devices[dev]['ip'] == host or dev == host:
            router = devices[dev]
            try:
                with ConnectHandler(**router) as connection:
                    connection.send_config_set('username ' + user + ' privilege ' 
                                            + privileges + ' password ' + password)
                    connection.save_config()
                break
            except:
                return {'status': 'No hay conexion al router'}
    return get_users(host)

def update_user(host, user, privileges=None, password=None):
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
        if devices[dev]['ip'] == host or dev == host:
            router = devices[dev]
            try:
                with ConnectHandler(**router) as connection:
                    connection.send_config_set(comand)
                    connection.save_config()
                break
            except:
                return {'status': 'No hay conexion al router'}
    return get_users(host)