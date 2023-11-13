from flask import Flask, jsonify, request
import json
import CRUDgeneral as crud
import CRUDdispositivo as crud_router

app =  Flask(__name__)


#Users endpoints TODO: Implement funtionalities 
@app.route("/usuarios")
def get_usuarios():
    usuarios = crud.get_users_all_routers()
    return json.dumps(usuarios)

@app.route("/usuarios", methods=["POST"])
def create_usuarios():
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud.create_user_all_routers(user, privilege, password)
    return json.dumps(usuarios)

@app.route("/usuarios", methods=["PUT"])
def update_usuarios():
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud.update_user_all_routers(user, privilege, password)
    return json.dumps(usuarios)

@app.route("/usuarios",methods=["DELETE"])
def delete_usuarios():
    user = request.form['user']
    usuarios = crud.delete_user_all_routers(user)
    return json.dumps(usuarios)


#Routes Endpoint TODO: Iplement get funtion
@app.route("/routes")
def get_routes():
    return "Hola"


#Routes Hostname Endpoint TODO: Iplement get funtion
@app.route("/routes/<hostname>")
def get_routes_hostname(hostname):
    return hostname

#Routes Hostname Interface Endpoint TODO: Iplement get funtion
@app.route("/routes/<hostname>/interfaces")
def get_routes_hostname_interface(hostname):
    return hostname+"interface"

#Crud users per router TODO: implement funtions
@app.route("/routes/<hostname>/usuarios")
def get_usuarios_router(hostname):
    usuarios = crud_router.get_users(hostname)
    return json.dumps(usuarios)

@app.route("/routes/<hostname>/usuarios", methods=["POST"])
def create_usuario_router(hostname):
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud_router.create_user(hostname, user, privilege, password)
    return json.dumps(usuarios)

@app.route("/routes/<hostname>/usuarios", methods=["PUT"])
def update_usuario_router(hostname):
    user = request.form['user']
    privilege = request.form['privilege']
    password = request.form['password']
    usuarios = crud_router.update_user(hostname, user,privilege, password)
    return json.dumps(usuarios)

@app.route("/routes/<hostname>/usuarios",methods=["DELETE"])
def delete_usuario_router(hostname):
    user = request.form['user']
    usuarios = crud_router.delete_user(hostname, user)
    return json.dumps(usuarios)


#Detect topology TODO: implement funtions
@app.route("/topologia")
def get_topologia():
    return "Hola"

@app.route("/topologia", methods=["POST"])
def create_daemon():
    return "Hola"

@app.route("/topologia", methods=["PUT"])
def update_daemon():
    return "Hola"

@app.route("/topologia",methods=["DELETE"])
def delete_daemon():
    return "Hola"

#Graphic topology TODO: implement funtions
@app.route("/topologia/grafica")
def get_topologiagrafico():
    return "Hola"


if __name__ == '__main__':
    app.run(debug=True)